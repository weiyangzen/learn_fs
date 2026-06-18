# Research: subset-b-001261

Grouped research for DMA driver files under `sources/distributed-fs/ceph-client/drivers/dma`. Each section is source-tree-aligned and intended for deterministic reconciliation into the matching per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/gpi.c -->
# sources/distributed-fs/ceph-client/drivers/dma/qcom/gpi.c

Purpose: implements the Qualcomm GPI DMAEngine provider used by QUP SPI/I2C clients on SDM/SM/SC SoCs. It exposes `DMA_SLAVE` channels through OF DMA translation, models each GPII as a paired TX/RX channel, and programs hardware TRE rings plus one event ring per GPII.

Important APIs/types/functions: `struct gpi_dev`, `struct gpii`, `struct gchan`, `struct gpi_ring`, and `struct gpi_desc` hold controller, instance, channel, ring, and virt-dma descriptor state. DMAEngine entry points are `gpi_alloc_chan_resources`, `gpi_free_chan_resources`, `gpi_prep_slave_sg`, `gpi_issue_pending`, `gpi_peripheral_config`, `gpi_terminate_all`, `gpi_pause`, and `gpi_resume`. Hardware command helpers include `gpi_send_cmd`, `gpi_alloc_ev_chan`, `gpi_alloc_chan`, `gpi_start_chan`, `gpi_stop_chan`, and `gpi_reset_chan`. Protocol encoders `gpi_create_spi_tre` and `gpi_create_i2c_tre` translate `struct gpi_spi_config` / `struct gpi_i2c_config` peripheral config into TRE sequences.

Control flow: `gpi_probe` maps registers, reads `dma-channels` and `dma-channel-mask`, applies match-data EE offsets, initializes all enabled GPIIs and channels, registers DMAEngine and `of_dma_controller_register`. `gpi_of_dma_xlate` assigns a free or matching-SEID GPII and returns either TX or RX virtual channel. Resource allocation creates coherent transfer rings and waits until both paired channels are configured, then allocates/configures the event ring, enables IRQs, allocates both channel contexts, and starts both channels. Prepared SG descriptors are limited to one SG entry and up to three TREs; `issue_pending` moves virt-dma descriptors to the issued list, copies TREs to the channel ring, and rings the doorbell. IRQs first handle control/error bits and defer event-ring completion to `gpi_ev_tasklet`; completion events advance ring read pointers, complete cookies, invoke callbacks with `dmaengine_result`, and free descriptors.

State/persistence: all runtime state is in memory and hardware registers: ring pointers, configured peripheral blob, GPII/channel PM states, IRQ mask state, and virt-dma lists. Coherent rings persist while channel resources are allocated. `ctrl_lock`, `pm_lock`, and per-vchan spinlocks guard command sequencing, register access, and descriptor lists.

Dependencies/integration: depends on Linux DMAEngine, virt-dma, OF DMA, coherent DMA allocation, QCOM GPI DT bindings, and `linux/dma/qcom-gpi-dma.h` protocol configs. Integrates with QUP SPI/I2C clients via DMA phandles and with platform IRQ resources.

Risks: paired-channel setup means one client can force allocation/start/stop of both TX/RX channels; non-UART terminate treats both channels as a group. `gpi_prep_slave_sg` assumes `gchan->config` starts with `set_config` and supports only `sg_len == 1`. Ring arithmetic and relaxed MMIO ordering depend on barriers; completion paths manually delete and `kfree` descriptors after callbacks. Error paths in `gpi_ch_init` use the current `gchan` in some cleanup loops, so channel-specific cleanup should be checked carefully during changes.

Test signals: boot/probe with each compatible and `dma-channel-mask`; OF DMA request sharing by SEID; SPI/I2C TX, RX, duplex, immediate small write, no-interrupt flags, and I2C multi-message paths; pause/resume/terminate while events are pending; IRQ storm/error/status logging; ring wraparound and insufficient-ring-space cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/gpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma.c

Purpose: implements the DMAEngine-facing Qualcomm HIDMA channel driver. It registers one memcpy/memset DMA channel per platform device, translates DMAEngine descriptors into low-level HIDMA TRE slots, handles runtime PM, sysfs/debug setup, wired IRQ or MSI setup, and teardown.

Important APIs/types/functions: `struct hidma_dev`, `struct hidma_chan`, and `struct hidma_desc` are declared in `hidma.h` and used here to manage descriptor lists (`free`, `prepared`, `queued`, `active`, `completed`). DMAEngine hooks include `hidma_alloc_chan_resources`, `hidma_free_chan_resources`, `hidma_prep_dma_memcpy`, `hidma_prep_dma_memset`, `hidma_tx_submit`, `hidma_issue_pending`, `hidma_tx_status`, `hidma_pause`, `hidma_resume`, and `hidma_terminate_all`. Platform lifecycle is `hidma_probe`, `hidma_remove`, and `hidma_shutdown`.

Control flow: probe enables runtime PM, maps TRCA/EVCA resources, chooses MSI support from ACPI match data, reads descriptor count, sets DMA mask, initializes the low-level ring device with `hidma_ll_init`, requests MSI or wired IRQ, creates one DMAEngine channel, registers DMAEngine, then initializes debugfs and `chid` sysfs. Channel resource allocation preallocates descriptors and reserves matching low-level TRE slots through `hidma_ll_request`. Prep functions pop a descriptor from `free`, program low-level TRE parameters, and move it to `prepared`; submit moves it to `queued` and assigns a cookie. `issue_pending` queues low-level requests, moves descriptors to `active`, sets `running`, grabs runtime PM, and starts hardware. The low-level callback moves a completed active descriptor to `completed`, calls `hidma_process_completed`, updates success/error status, runs dependencies, returns the descriptor to `free`, invokes callbacks, and releases runtime PM autosuspend.

State/persistence: descriptor list membership is the main software state. `last_success` distinguishes successful cookies from DMAEngine-complete-but-error cookies; `paused`, `allocated`, and `running` report channel state. Runtime PM references are taken per active descriptor and released from completion/terminate paths.

Dependencies/integration: depends on `hidma_ll.c` for TRE ring programming and IRQ consumption, `hidma_dbg.c` for debugfs, Linux DMAEngine, ACPI match IDs `QCOM8061/8062/8063`, MSI APIs under `CONFIG_GENERIC_MSI_IRQ`, and platform resources.

Risks: `hidma_issue_pending` uses `list_first_entry(&mchan->active, ...)` after queuing; callers rely on active not being empty. Low-level `hidma_ll_request` invokes the callback during allocation, so the callback path must tolerate descriptors not yet submitted. Termination invokes callbacks with `NULL` result and reinitializes hardware, so clients must handle abort semantics. Runtime PM error handling schedules a tasklet fallback but still needs careful balance checks.

Test signals: memcpy/memset DMAEngine tests, descriptor-count override, MSI and wired IRQ modes, runtime autosuspend/resume around active transfers, pause/resume status reporting, terminate-all while queued/active/completed lists are populated, ACPI capability variants, and debugfs/sysfs presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma.h -->
# sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma.h

Purpose: shared internal header for Qualcomm HIDMA channel, low-level, and debug code. It defines the TRE layout, low-level ring device state, DMAEngine channel/device state, and cross-file function prototypes.

Important APIs/types/functions: `enum tre_type` selects HIDMA memcpy and memset transaction types. `struct hidma_tre` represents a low-level request slot with allocation state, callback, local TRE words, ring index, interrupt flags, and error fields. `struct hidma_lldev` owns hardware-facing state: TRCA/EVCA mappings, TRE/EVRE coherent rings, pending TRE table, processed offsets, write offset, tasklet, FIFO, and channel states. `struct hidma_desc` wraps `dma_async_tx_descriptor` with a low-level TRE channel number. `struct hidma_chan` owns DMAEngine lists and per-channel status. `struct hidma_dev` owns platform resources, the `dma_device`, IRQ/MSI metadata, debugfs/sysfs state, and issue tasklet.

Control flow: the header expresses the layering boundary. `hidma.c` allocates `hidma_desc` objects and calls `hidma_ll_request`, `hidma_ll_set_transfer_params`, `hidma_ll_queue_request`, and `hidma_ll_start`. `hidma_ll.c` updates status and invokes callbacks. `hidma_dbg.c` reads both `hidma_chan` lists and `hidma_lldev` internals.

State/persistence: all fields are volatile runtime driver state; no persistent storage is involved. Synchronization is expected through `hidma_chan.lock`, `hidma_lldev.lock`, atomics in `hidma_tre`, and runtime PM in the caller.

Dependencies/integration: includes `kfifo`, `interrupt`, and `dmaengine`; assumes Linux DMAEngine cookie/callback semantics and platform MMIO.

Risks: because this header exposes internals across four implementation files, structure changes affect DMAEngine logic, low-level IRQ handling, and debugfs output together. `tre_local` is sized as `HIDMA_TRE_SIZE / sizeof(u32) + 1`, while transfer programming uses fixed index constants; layout changes must preserve hardware format.

Test signals: compile all HIDMA objects together, run memcpy/memset transfer tests, inspect debugfs output for coherent field values, and exercise error completion to confirm `err_info`/`err_code` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_dbg.c -->
# sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_dbg.c

Purpose: adds debugfs inspection for Qualcomm HIDMA devices and channels. It is observational only and dumps descriptor/TRE, ring, and resource state for diagnosis.

Important APIs/types/functions: `hidma_ll_chstats` prints one TRE slot, including allocation, queue state, error fields, callback pointer, source/destination DMA addresses, and length. `hidma_ll_devstats` prints low-level device state, ring addresses, ring sizes, processed offsets, and pending TRE count. `hidma_chan_show` prints channel-level paused/signature state and walks `prepared`, `active`, and `completed` lists. `hidma_dma_show` prints descriptor count and TRCA/EVCA resource addresses. `hidma_debug_init` creates debugfs directories and files; `hidma_debug_uninit` removes them.

Control flow: after `hidma.c` registers the DMAEngine channel, `hidma_debug_init` creates a top-level directory named after the device, a `chanN/stats` file for each DMAEngine channel, and a device-level `stats` file. Reading channel stats resumes the device with runtime PM, prints list and low-level state, then marks last busy and autosuspends.

State/persistence: no persistent state beyond debugfs dentries and generated channel debug names. It reads live driver lists without taking the HIDMA channel lock while iterating, so output is diagnostic and may race with active transfers.

Dependencies/integration: depends on debugfs, seq_file `DEFINE_SHOW_ATTRIBUTE`, runtime PM, and internal structures from `hidma.h`.

Risks: exposes kernel virtual addresses and callback pointers through debugfs, suitable for privileged debugging only. List iteration without locks can report transient state. Runtime PM calls in read path can perturb power state during diagnostics.

Test signals: debugfs directory/files appear after probe, disappear after remove, reads succeed during idle and active transfers, and `pending_tre_count`/offsets change consistently under DMAEngine tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_ll.c -->
# sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_ll.c

Purpose: low-level HIDMA hardware driver responsible for TRE/EVRE ring allocation, MMIO setup, channel enable/disable/reset, interrupt cause handling, completion extraction, and callback handoff to the DMAEngine layer.

Important APIs/types/functions: exported-to-internal functions include `hidma_ll_init`, `hidma_ll_uninit`, `hidma_ll_setup`, `hidma_ll_request`, `hidma_ll_free`, `hidma_ll_set_transfer_params`, `hidma_ll_queue_request`, `hidma_ll_start`, `hidma_ll_disable`, `hidma_ll_enable`, `hidma_ll_status`, `hidma_ll_inthandler`, `hidma_ll_inthandler_msi`, and `hidma_cleanup_pending_tre`. Internal helpers include `hidma_ll_reset`, `hidma_handle_tre_completion`, `hidma_post_completed`, and `hidma_ll_tre_complete`.

Control flow: initialization allocates a TRE pool, pending-TRE table, coherent TRE ring, coherent EVRE ring, and handoff FIFO, aligns ring bases, programs hardware via `hidma_ll_setup`, and enables IRQs. Requests reserve TRE slots atomically and seed fixed configuration bits. Queueing copies local TRE words to the next ring slot, records the pending TRE, increments pending count, and advances the write offset. `hidma_ll_start` rings the TRCA doorbell. IRQ handling masks status with enabled bits; error causes disable hardware and synthesize error completions for all pending TREs, while normal causes clear interrupts and consume EVREs up to the hardware write pointer. Completions map ordered EVREs back to pending TREs by processed offset, update error code/info, enqueue to the FIFO, and schedule a tasklet that invokes requester callbacks.

State/persistence: runtime state is ring offsets, pending table entries, pending count, low-level channel states, enabled/MSI flag, and per-TRE allocation/error fields. No persistence survives device removal.

Dependencies/integration: used by `hidma.c`; depends on coherent DMA memory, `readl_poll_timeout`, Linux kfifo/tasklets, and hardware ordering guarantees documented in the ISR comments.

Risks: comments explicitly rely on HIDMA-specific interrupt ordering and relaxed MMIO assumptions. `hidma_ll_request` reserves only `nr_tres - 1` entries to keep one ring slot empty. Error cleanup loops until pending count reaches zero and depends on offset/table consistency. `hidma_ll_init` calls setup before initializing `lock` and tasklet, so changes around setup/IRQ enable order need care.

Test signals: ring alignment on varied DMA addresses, queue wraparound, normal completion ordering, MSI cause bit handling, wired IRQ status clearing, injected hardware error bits, disable/enable/reset polling timeouts, and synthesized completions during terminate/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_ll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_mgmt.c -->
# sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_mgmt.c

Purpose: platform management driver for Qualcomm HIDMA common hardware registers. It validates and programs global DMA QoS, max burst, max transaction, reset-timeout, hardware-version, and channel arbitration settings before per-channel HIDMA engines operate.

Important APIs/types/functions: `struct hidma_mgmt_dev` is defined in `hidma_mgmt.h`. `hidma_mgmt_setup` is exported and re-applies all validated settings. `hidma_mgmt_probe` reads ACPI/device properties and module-param overrides, maps the management register block, starts hardware, initializes sysfs via `hidma_mgmt_init_sys`, and enables runtime PM. Module parameters allow overriding max write/read request sizes and max write/read transactions.

Control flow: probe enables runtime PM, maps resource 0, obtains IRQ presence, allocates management state, reads `dma-channels`, `channel-reset-timeout-cycles`, `max-write-burst-bytes`, `max-read-burst-bytes`, `max-write-transactions`, and `max-read-transactions`, allocates per-channel priority/weight arrays, calls `hidma_mgmt_setup`, sets `HIDMA_CFG_OFFSET` bit 0 to start hardware, creates sysfs knobs, and stores drvdata. `hidma_mgmt_setup` validates power-of-two 128..1024 burst sizes, transaction masks, priority values, and weight range, then writes max bus request length, transaction limits, QoS registers per channel, reset timeout, and reads hardware revision.

State/persistence: management values are kept in `hidma_mgmt_dev` and programmed to MMIO registers. Sysfs setters update the in-memory value, call setup, and roll back on validation/programming failure.

Dependencies/integration: uses platform property APIs, runtime PM, MMIO, module parameters, `hidma_mgmt_sys.c` for sysfs, and ACPI ID `QCOM8060`. Per-channel `hidma.c` devices depend on this global management block being configured on systems that expose it.

Risks: probe obtains an IRQ but does not request it in this file, so the IRQ resource acts as a presence/firmware contract. Priority/weight arrays are zero-initialized, and setup converts zero weight to one. Read-only-looking sysfs attributes are still wired with store callbacks internally, but modes mostly restrict writes except per-channel knobs.

Test signals: invalid DT/ACPI properties reject probe; module parameter overrides program expected registers; sysfs changes update registers and roll back on invalid values; runtime PM balances on setup; hardware revision appears in logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_mgmt.h -->
# sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_mgmt.h

Purpose: shared header for HIDMA management common-register and sysfs code. It defines `struct hidma_mgmt_dev` and prototypes the setup/sysfs entry points.

Important APIs/types/functions: `struct hidma_mgmt_dev` stores hardware revision, max transaction/request limits, channel count, reset timeout, per-channel priority and weight arrays, mapped register base/size, sysfs channel kobject roots, and owning platform device. `hidma_mgmt_setup` programs validated state to hardware; `hidma_mgmt_init_sys` creates sysfs controls.

Control flow: `hidma_mgmt.c` allocates and populates this structure at probe, calls setup, then passes it to `hidma_mgmt_sys.c`. Sysfs writes mutate fields and call setup to reprogram hardware.

State/persistence: all fields are runtime management state mirrored into MMIO; no persistent storage is present. `chroots` is allocated per channel for sysfs hierarchy.

Dependencies/integration: relies on platform device lifetime and MMIO access from implementation files. It intentionally has no include guard in the shown file, so double-inclusion risks should be considered if includes expand.

Risks: because sysfs and setup share the same mutable structure without explicit locking in this header contract, concurrent writes could interleave unless higher-level sysfs serialization is sufficient for the intended use. Adding fields requires updating both property parsing and sysfs.

Test signals: compile both management objects, probe with several `dma-channels` values, inspect sysfs channel tree, and verify register updates after sysfs writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_mgmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_mgmt_sys.c -->
# sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_mgmt_sys.c

Purpose: sysfs support for the HIDMA management driver. It exposes global management parameters and per-channel arbitration knobs, and reprograms hardware through `hidma_mgmt_setup` when writable values change.

Important APIs/types/functions: `struct hidma_chan_attr` wraps a per-channel kobject attribute with channel index and management pointer. `struct hidma_mgmt_fileinfo` maps global sysfs names to generated get/set functions. Macros `IMPLEMENT_GETSET` and `DECLARE_ATTRIBUTE` create common attribute handlers. Key functions are `show_values`, `set_values`, `show_values_channel`, `set_values_channel`, `create_sysfs_entry`, `create_sysfs_entry_channel`, and exported `hidma_mgmt_init_sys`.

Control flow: `hidma_mgmt_init_sys` allocates `chroots`, creates a `chanops` kobject under the device, creates `chanN` children for all channels, installs global files for revision/channel/limit values, and installs writable `priority` and `weight` files under each channel. Global setters parse an integer, locate the fileinfo entry, update the field, call `hidma_mgmt_setup`, and roll back on failure. Per-channel setters do the same for indexed priority/weight.

State/persistence: sysfs state is represented by devm-allocated attributes and kobjects. Values live in `hidma_mgmt_dev`; hardware is updated immediately on successful writes. There is no explicit remove function in this file, relying on device/kobject lifetime patterns.

Dependencies/integration: depends on `hidma_mgmt.c` for validation/programming and platform device drvdata. Uses sysfs/kobject APIs and standard numeric parsing.

Risks: kobject cleanup is not explicit in this file, so removal behavior should be checked against the wider driver lifecycle. Many global attributes are mode `S_IRUGO`, yet their fileinfo includes setters; permission bits rather than handler absence enforce read-only behavior. Concurrent sysfs writes can call full hardware setup repeatedly.

Test signals: sysfs tree creation for every channel, read all global files, write valid/invalid priority and weight values, verify rollback on invalid setup, and unbind/rebind under sysfs leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/hidma_mgmt_sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/qcom_adm.c -->
# sources/distributed-fs/ceph-client/drivers/dma/qcom/qcom_adm.c

Purpose: Qualcomm ADM DMAEngine slave driver. It exposes 16 DMA slave channels, builds ADM command pointer/descriptor lists for flow-controlled and non-flow-controlled peripheral transfers, and integrates with OF DMA using channel and optional CRCI specifiers.

Important APIs/types/functions: hardware descriptor formats are `struct adm_desc_hw_box` and `struct adm_desc_hw_single`. Driver state is `struct adm_async_desc`, `struct adm_chan`, and `struct adm_device`. DMAEngine hooks are `adm_free_chan`, `adm_prep_slave_sg`, `adm_slave_config`, `adm_issue_pending`, `adm_tx_status`, and `adm_terminate_all`. Hardware helpers include `adm_process_fc_descriptors`, `adm_process_non_fc_descriptors`, `adm_start_dma`, `adm_dma_irq`, and `adm_dma_xlate`.

Control flow: probe maps registers, reads `qcom,ee`, enables core/interface clocks, toggles reset controls, initializes channels, resets CRCIs, configures client interfaces and low-power global control, requests the shared IRQ, registers DMAEngine, and registers OF DMA. Prep validates direction, derives burst/CRCI from `dma_slave_config` and optional `qcom_adm_peripheral_config`, counts needed box/single descriptors, allocates and maps a command-pointer-list buffer, fills descriptors for each SG entry, and returns a virt-dma descriptor. Issue pending starts the first queued descriptor if no current transfer is active. IRQ scans security-domain status for all channels, validates result registers, records errors on failed/flushed results, completes current virt-dma cookie, and starts the next descriptor.

State/persistence: per-channel `curr_txd`, `slave`, `crci`, `mux`, `error`, and `initialized` hold runtime state. Descriptor memory is allocated per transaction and DMA-mapped until virt-dma frees it. Hardware channel configuration is lazily initialized on first start.

Dependencies/integration: depends on clocks, resets, OF DMA, `linux/dma/qcom_adm.h` peripheral config, scatterlist DMA mappings, and virt-dma. Clients use one-cell or two-cell DMA specifiers.

Risks: `common.directions` uses `BIT(DMA_DEV_TO_MEM | DMA_MEM_TO_DEV)`, which is unusual because other drivers use `BIT(DMA_DEV_TO_MEM) | BIT(DMA_MEM_TO_DEV)`; this should be checked if direction capability reporting changes. Residue reporting is descriptor-granularity only. Flow-control descriptor count math depends on valid nonzero burst. IRQ loop scans fixed `ADM_MAX_CHANNELS` even if clients use fewer.

Test signals: OF DMA xlate with one and two args, flow-controlled transfer with valid/invalid CRCI and burst, non-flow-control large SG split at `ADM_MAX_XFER`, IRQ completion/error/flush results, clock/reset failure unwind, and remove while descriptors are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/qcom/qcom_adm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sa11x0-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/sa11x0-dma.c

Purpose: DMAEngine slave/cyclic driver for SA-11x0 DMA hardware. It maps 16 named virtual peripheral directions onto six physical DMA channels and uses double-buffer hardware registers to stream SG and cyclic transfers.

Important APIs/types/functions: `struct sa11x0_dma_sg`, `struct sa11x0_dma_desc`, `struct sa11x0_dma_chan`, `struct sa11x0_dma_phy`, and `struct sa11x0_dma_dev` model split SG fragments, virtual channels, physical channels, and controller state. DMAEngine hooks include `sa11x0_dma_prep_slave_sg`, `sa11x0_dma_prep_dma_cyclic`, `sa11x0_dma_device_config`, `sa11x0_dma_issue_pending`, `sa11x0_dma_tx_status`, `sa11x0_dma_device_pause`, `sa11x0_dma_device_resume`, and `sa11x0_dma_device_terminate_all`.

Control flow: probe ioremaps the register block, initializes six physical channels and IRQs, clears hardware, registers DMAEngine channels from static peripheral descriptors, and advertises filter-map entries for IR and SSP clients. Prep validates native channel direction, alignment, bus width, burst, and nonzero length, splits large SG/cyclic periods into hardware-sized fragments, and creates virt-dma descriptors. `issue_pending` moves submitted descriptors to issued and queues virtual channels needing a physical channel. A controller tasklet assigns free physical channels to pending virtual channels, starts descriptors, and releases physical channels when no more compatible work remains. IRQs clear DONE/ERROR bits and, under the virtual channel lock, complete fragment A/B events, complete cookies or cyclic callbacks, and load more fragments.

State/persistence: virtual channel state includes assigned physical channel and status. Physical channel state tracks active/load descriptors, fragment indices, saved suspend registers, and register base. Pending virtual channels live on a controller list protected by `d->lock`.

Dependencies/integration: depends on legacy platform resources/IRQs, DMAEngine filter maps, virt-dma, tasklets, and SA-11x0 DDAR/DCSR hardware semantics.

Risks: manual physical-channel multiplexing and double-buffer state are concurrency-sensitive. Residue calculation reads active hardware address and walks split fragments, so it is best-effort during races. System suspend saves buffer register order depending on BIU state and resumes only if descriptors remain. Only 1- or 2-byte widths and bursts 4/8 are accepted.

Test signals: slave SG and cyclic audio-style transfers, all named channel filters, physical-channel contention among more than six virtual channels, pause/resume/terminate, suspend/resume mid-transfer, error IRQ logging, residue before/during/after transfer, and alignment rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sa11x0-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/Kconfig

Purpose: Kconfig entry for the SiFive Platform DMA controller driver.

Important APIs/types/functions: defines `config SF_PDMA` as a tristate option named "Sifive PDMA controller driver". It depends on `HAS_IOMEM` and selects `DMA_ENGINE` plus `DMA_VIRTUAL_CHANNELS`.

Control flow: when enabled as built-in or module, the build system compiles `sf-pdma.o` through the adjacent Makefile. Selecting DMAEngine and virtual channels ensures required framework support for `sf-pdma.c`.

State/persistence: no runtime state; this is build configuration only.

Dependencies/integration: integrates with the kernel DMAEngine Kconfig hierarchy and gates the SiFive/Microchip PDMA platform driver.

Risks: the option does not depend on `OF`, even though the driver uses OF match/controller registration; this may be acceptable through compile-time stubs or broader DMAEngine configuration but should be considered in randconfig failures.

Test signals: `allyesconfig`, `allmodconfig`, `COMPILE_TEST` style builds, and configurations with `HAS_IOMEM=n` confirming the option is hidden.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/Makefile

Purpose: build rule for the SiFive PDMA DMAEngine driver.

Important APIs/types/functions: `obj-$(CONFIG_SF_PDMA) += sf-pdma.o` builds the single implementation file when the Kconfig symbol is enabled.

Control flow: kernel kbuild includes this object as built-in or module according to `CONFIG_SF_PDMA`.

State/persistence: no runtime state.

Dependencies/integration: depends on the parent DMA Makefile including this directory and the Kconfig symbol being visible.

Risks: there are no split objects, so any future helper files must be added here or they will not build.

Test signals: verify `CONFIG_SF_PDMA=y` links built-in and `CONFIG_SF_PDMA=m` emits the module object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/sf-pdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/sf-pdma.c

Purpose: SiFive FU540/Microchip MPFS Platform DMAEngine memcpy driver. It exposes memory-to-memory DMA channels, programs per-channel PDMA registers, handles done/error IRQ pairs, and integrates with OF DMA by channel ID.

Important APIs/types/functions: `struct sf_pdma`, `struct sf_pdma_chan`, `struct sf_pdma_desc`, and `struct pdma_regs` are defined in `sf-pdma.h`. DMAEngine hooks are `sf_pdma_alloc_chan_resources`, `sf_pdma_free_chan_resources`, `sf_pdma_tx_status`, `sf_pdma_prep_dma_memcpy`, `sf_pdma_slave_config`, `sf_pdma_terminate_all`, and `sf_pdma_issue_pending`. IRQ/tasklet flow uses `sf_pdma_done_isr`, `sf_pdma_err_isr`, `sf_pdma_donebh_tasklet`, and `sf_pdma_errbh_tasklet`.

Control flow: probe reads `dma-channels` or defaults to four, applies platform quirks to transfer type, maps registers, requests two IRQs per channel, initializes channel register pointers and tasklets, sets DMAEngine memcpy capabilities, sets a 64-bit DMA mask when possible, registers DMAEngine, and registers OF DMA. Prep allocates one descriptor, validates nonzero len/src/dest, fills transfer type/size/src/dst, and prepares it with virt-dma. Issue pending starts the first issued descriptor if no descriptor is active. Transfer programming writes type, size, destination, source, marks status in progress, and sets claim/run/interrupt bits. Done IRQ clears done status and either schedules completion if residue is zero or adjusts descriptor addresses/size and restarts for remaining bytes. Error IRQ clears error status and schedules retry/failure tasklet.

State/persistence: each channel keeps one active `desc`, current status, retry/error flags, register pointers, IRQ numbers, and a copied slave config. Descriptors are dynamically allocated and freed by virt-dma. No persistent storage.

Dependencies/integration: depends on OF DMA, platform IRQ resources, MMIO, virt-dma, DMAEngine, and optional match-data quirk `PDMA_QUIRK_NO_STRICT_ORDERING` for MPFS.

Risks: error tasklet invokes callback directly on final failure without completing/freeing the virt-dma descriptor in the same path, so changes should inspect error lifecycle carefully. `sf_pdma_desc_residue` scans `desc_submitted` and may not report active descriptors as expected. Done path mutates active descriptor for partial residue. `descriptor_reuse = true` should be checked against descriptor freeing semantics.

Test signals: DMA memcpy selftests across all channels, partial completion/residue restart, injected error IRQ with retry exhaustion, OF DMA channel selection, MPFS strict-ordering quirk, terminate/free while active, and module remove after queued work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/sf-pdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/sf-pdma.h -->
# sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/sf-pdma.h

Purpose: private header for the SiFive PDMA driver. It defines register offsets, control/status masks, transfer constants, channel/controller data structures, and platform quirk data used by `sf-pdma.c`.

Important APIs/types/functions: register constants describe per-channel control, transfer type/size, source/destination, active type, residue, and current-address registers. `struct pdma_regs` caches MMIO addresses. `struct sf_pdma_desc` wraps one virt-dma descriptor and transfer tuple. `enum sf_pdma_pm_state`, `struct sf_pdma_chan`, `struct sf_pdma`, and `struct sf_pdma_driver_platdata` define channel state, flexible-array controller state, and match-data quirks.

Control flow: `sf_pdma_setup_chans` fills `pdma_regs` from `SF_PDMA_REG_BASE`, initializes `sf_pdma_chan`, and binds each virtual channel to the shared `dma_device`. Transfer functions consume `sf_pdma_desc` fields and program corresponding registers.

State/persistence: all structures are runtime-only and allocated by probe. `PDMA_MAX_NR_CH` caps hardware channels at four; `MAX_RETRY` defines one error retry. Control masks define claim/run/interrupt/status bit usage.

Dependencies/integration: includes DMAEngine, dma-direction, internal DMAEngine helper, and virt-dma. It assumes 64-bit register accesses may be synthesized by the C file on architectures without `readq/writeq`.

Risks: `PDMA_BASE_ADDR` is defined but not used by the implementation, so register base comes from platform resources. Header-exposed fields such as `mappedbase`, `attr`, and DMA device address fields are currently unused, which can mislead future changes.

Test signals: compile with sparse/unused-field checks, verify channel count limits, register offsets against hardware manual, and exercise residue/current-address MMIO reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/sf-pdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sh/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma/sh/Kconfig

Purpose: Kconfig menu for Renesas/SuperH DMAEngine drivers under `drivers/dma/sh`.

Important APIs/types/functions: symbols include helper `RENESAS_DMA`, base helper `SH_DMAE_BASE`, controller options `SH_DMAE`, `RCAR_DMAC`, `RENESAS_USB_DMAC`, and `RZ_DMAC`. Several select `DMA_VIRTUAL_CHANNELS` or `RENESAS_DMA`.

Control flow: enabling architecture-appropriate options controls which objects in the adjacent Makefile are built. `SH_DMAE_BASE` gates legacy SuperH DMA support and enforces dependencies on `SUPERH`, `SH_DMA`, and `SH_DMA_API`. R-Car, USB DMAC, and RZ DMAC are available on `ARCH_RENESAS` or compile-test.

State/persistence: no runtime state; build-time configuration only.

Dependencies/integration: integrates Renesas DMA drivers with DMAEngine and architecture config symbols.

Risks: dependency expressions around SuperH legacy APIs are subtle; relaxing them could create conflicting DMA APIs. Some options select only `RENESAS_DMA`, while USB/RZ also select virtual channels according to their implementation needs.

Test signals: randconfig for `SUPERH`, `ARCH_RENESAS`, and `COMPILE_TEST`; verify each enabled symbol builds the intended object and selects DMAEngine support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sh/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sh/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/sh/Makefile

Purpose: kbuild rules for Renesas/SuperH DMAEngine helper and controller objects.

Important APIs/types/functions: builds `shdma-base.o` for `CONFIG_SH_DMAE_BASE`; assembles `shdma.o` from `shdmac.o` for `CONFIG_SH_DMAE`; builds `rcar-dmac.o`, `usb-dmac.o`, and `rz-dmac.o` for their respective symbols.

Control flow: Kconfig selections decide which objects enter the kernel or modules. The intermediate `shdma-y`/`shdma-objs` variables make the legacy SH DMA controller extensible if more objects are added.

State/persistence: no runtime state.

Dependencies/integration: depends on Kconfig symbol names in `sh/Kconfig` and parent DMA kbuild inclusion.

Risks: adding helper files for `shdma.o` requires updating `shdma-y`. Object names must stay aligned with implementation filenames in this directory.

Test signals: per-symbol build tests for `SH_DMAE_BASE`, `SH_DMAE`, `RCAR_DMAC`, `RENESAS_USB_DMAC`, and `RZ_DMAC`, including module builds where symbols are tristate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/sh/Makefile -->
