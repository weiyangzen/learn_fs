# Research: subset-b-001256

Grouped research for `subset-b-001256`. Each section preserves the source path in its title and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/irq.c -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/irq.c

Purpose: implements Intel IDXD/DSA/IAA interrupt-side recovery and completion processing. It handles the miscellaneous MSI-X vector for device errors, command completion, performance counter overflow, event-log notifications, interrupt-handle revocation, and halt states, plus the per-workqueue threaded IRQ used to retire kernel descriptors that requested completion interrupts.

Important APIs, types, and functions: exported entry points are `idxd_misc_thread()`, `idxd_wq_thread()`, and `idxd_queue_int_handle_resubmit()`. Internal work items include `idxd_device_reinit()`, `idxd_device_flr()`, `idxd_int_handle_revoke()`, `idxd_evl_fault_work()`, and `idxd_int_handle_resubmit_work()`. `struct idxd_resubmit` carries descriptors that must be retried after an invalid interrupt handle; `struct idxd_int_handle_revoke` carries the device for deferred interrupt-handle refresh. The file relies on `struct idxd_irq_entry` pending and work lists, event-log entries from `registers.h`, and descriptor completion helpers from the wider IDXD driver.

Control flow: `idxd_misc_thread()` reads and acknowledges `IDXD_INTCAUSE`, then branches by cause. Halt interrupts call `idxd_halt()`, which either schedules software reinit, schedules PCI FLR, or quiesces/unmaps all WQs for unrecoverable reset types. Software errors snapshot `SWERR`, acknowledge valid/overflow bits, and wake affected user WQ error waiters. Command interrupts complete `idxd->cmd_done`; perfmon overflow calls `perfmon_counter_overflow()`; event-log interrupts drain hardware EVL entries under `evl->lock`. EVL entries that need user completion-record repair allocate fault work and copy the hardware completion record back to the PASID address space asynchronously. `idxd_wq_thread()` is a single-consumer loop over a lockless producer list and a protected work list: completed descriptors are retired, incomplete descriptors are staged for later, and software abort status gets special handling.

State and persistence: persistent state includes `idxd->state`, `idxd->sw_err`, WQ enable maps, interrupt handles, event-log head/tail and bitmap state, per-WQ wait queues, and pending descriptor lists. Workqueue jobs intentionally persist beyond the IRQ thread to perform resets, FLR, fault completion-copy, and resubmission outside hard interrupt context. Descriptor completion changes allocator state and user-visible DMA completion state.

Dependencies and integration: integrated with PCI FLR, IDXD command/config/reset helpers, IOMMU PASID handling, IDXD cdev/user counters, perf PMU overflow handling, workqueue infrastructure, threaded MSI-X setup in `init.c`, and submission code in `submit.c`. It also consumes DSA/IAA completion record layout details through `idxd->data` offsets.

Risks and test signals: high-risk areas are interrupt-handle revoke ordering, list migration between lockless pending and locked work lists, event-log completion-record copying to exited or shared address spaces, and reset/FLR while descriptors are outstanding. Test by forcing command completion, SWERR, halt software reset, halt FLR, perf counter overflow, invalid interrupt-handle completion, ENQCMDS resubmit failure, user EVL page-fault records, and concurrent descriptor submission while WQ active refs are killed and revived.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/perfmon.c -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/perfmon.c

Purpose: exposes IDXD hardware performance monitoring counters as a Linux perf PMU named per device (`dsaN` or `iaxN`). It maps perf event `config`/`config1` fields into event category, event encoding, and optional hardware filters, programs counter MMIO registers, maintains software-extended counts across overflow, and registers/unregisters the PMU during IDXD device lifetime.

Important APIs, types, and functions: public functions are `perfmon_pmu_init()`, `perfmon_pmu_remove()`, and `perfmon_counter_overflow()`. PMU callbacks include `perfmon_pmu_event_init()`, `perfmon_pmu_event_add()`, `perfmon_pmu_event_del()`, `perfmon_pmu_event_start()`, `perfmon_pmu_event_stop()`, `perfmon_pmu_event_update()`, `perfmon_pmu_enable()`, and `perfmon_pmu_disable()`. `DEFINE_PERFMON_FORMAT_ATTR()` creates sysfs format files for `event_category`, `event`, `filter_wq`, `filter_tc`, `filter_pgsz`, `filter_sz`, and `filter_eng`.

Control flow: initialization rejects hardware without a perfmon table, counters, counter width, overflow interrupts, freeze support, event categories, or with per-counter capabilities the driver does not understand. It resets configuration/counters, records capabilities from `PERFCAP`, trims unsupported filter format attributes, initializes `struct pmu`, and calls `perf_pmu_register()`. Event init validates type, CPU, no sampling, and group schedulability. Event add collects active group events, allocates a counter bit in `used_mask`, stores original counter config, and optionally starts. Start writes supported filters, snapshots `CNTRDATA`, and enables `CNTRCFG` with overflow interrupt. Stop removes the event from `event_list`, clears enable, optionally updates count, and frees the counter bit. Overflow processing reads `OVFSTATUS`, updates each affected event, clears bits, and loops with a failsafe.

State and persistence: `struct idxd_pmu` persists under `idxd->idxd_pmu`, holding PMU name, counter count/width, supported filters/categories, `event_list`, active event count, and `used_mask`. `perf_event.hw.prev_count` persists the last raw hardware count so deltas can be sign-extended to the configured counter width. Hardware state persists in perfmon config, freeze, overflow, filter, and counter registers until reset or reprogramming.

Dependencies and integration: depends on `perfmon.h` register helpers, `registers.h` perf capability layouts, Linux perf core, IDXD MMIO register base/offset discovery, and `idxd_misc_thread()` forwarding `IDXD_INTC_PERFMON_OVFL` to `perfmon_counter_overflow()`. It is compiled conditionally through declarations in `idxd.h`.

Risks and test signals: risks include global mutation of `perfmon_format_attrs` when filters are absent, stale `event_list` entries during overflow, group scheduling mismatches, and missed overflow loops on very narrow counters. Test with `perf list`, `perf stat -e dsa*/.../`, unsupported filters, grouped events exceeding hardware counters, module removal while events are active, overflow interrupt delivery, PMU freeze/unfreeze, and guest configurations that advertise no counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/perfmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/perfmon.h -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/perfmon.h

Purpose: provides the IDXD perfmon support definitions shared by the PMU implementation. It defines conversions from perf PMU objects back to IDXD objects, event/filter encodings, counter-control constants, and MMIO address macros for the perfmon register table.

Important APIs, types, and macros: inline helpers `event_to_pmu()`, `event_to_idxd()`, and `pmu_to_idxd()` recover `struct idxd_pmu` and `struct idxd_device` from perf core objects. `enum dsa_perf_events` documents high-level DSA categories, while `enum filter_enc` indexes filter register slots. Register helpers include `PERFMON_TABLE_OFFSET()`, `PERFMON_REG_OFFSET()`, `PERFCAP_REG()`, `PERFRST_REG()`, `OVFSTATUS_REG()`, `PERFFRZ_REG()`, `FLTCFG_REG()`, `CNTRCFG_REG()`, `CNTRDATA_REG()`, `CNTRCAP_REG()`, and `EVNTCAP_REG()`. `DEFINE_PERFMON_FORMAT_ATTR()` generates perf sysfs format attributes.

Control flow: this header has no runtime control flow beyond container conversions and macro-generated sysfs show functions. The address macros compose `idxd->reg_base`, `idxd->perfmon_offset`, fixed offsets from `registers.h`, counter index, and filter index. `perfmon.c` uses these helpers for capability probing, counter reset, filter programming, counter reads, overflow clearing, and PMU registration.

State and persistence: no independent state is stored here. The constants define persistent hardware bit meanings such as `CONFIG_RESET`, `CNTR_RESET`, `COUNTER_FREEZE`, `COUNTER_UNFREEZE`, `CNTRCFG_ENABLE`, and `CNTRCFG_IRQ_OVERFLOW`. The macro-generated attributes are static objects in the translation unit that includes the macro.

Dependencies and integration: depends on Linux perf, PCI, DMAengine, cdev, wait, UUID, sbitmap, and IDXD register definitions. It assumes `struct idxd_pmu` contains `struct pmu pmu` and `struct idxd_device *idxd`, as defined in `idxd.h`. It ties the perf PMU ABI strings to `perf_event_attr.config` and `config1` bit layouts consumed by `perfmon.c`.

Risks and test signals: the primary risks are ABI drift between format strings and `union event_cfg`/`union filter_cfg`, incorrect register offset arithmetic, and static attribute-name collisions if used outside its intended file. Test by checking `/sys/bus/event_source/devices/dsa*/format/*`, verifying perf encodes filters into expected registers, probing multiple devices, and validating counter data with known workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/perfmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/registers.h -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/registers.h

Purpose: defines the Intel IDXD MMIO, table, command, error, workqueue, group, perfmon, DSA capability, and event-log register contract used by the DSA/IAA driver. It is the central hardware ABI map for all IDXD code that probes capabilities, configures WQs/groups, submits commands, handles interrupts, exposes sysfs state, and decodes event-log entries.

Important APIs, types, and macros: it defines PCI IDs, BAR numbers, device versions, register offsets, interrupt cause bits, command opcodes/status errors, and table-offset helpers. Capability unions include `gen_cap_reg`, `wq_cap_reg`, `group_cap_reg`, `engine_cap_reg`, `idxd_perfcap`, `idxd_evntcap`, `idxd_cntrcfg`, `idxd_cntrdata`, `dsacap0_reg`, `dsacap1_reg`, and `dsacap2_reg`. Configuration layouts include `gencfg_reg`, `genctrl_reg`, `grpcfg`, `group_flags`, `wqcfg`, `evlcfg_reg`, and `msix_perm`. Error and event-log structures include `sw_err_reg`, `evl_status_reg`, `__evl_entry`, `dsa_evl_entry`, and `iax_evl_entry`.

Control flow: there is no direct execution, but the definitions drive control flow elsewhere. `irq.c` branches on `IDXD_INTC_*`, decodes `gensts_reg`, snapshots `sw_err_reg`, and walks `evl_status_reg`/`__evl_entry`. `sysfs.c` exposes capability and config fields, with visibility checks based on version and capability bits. `perfmon.c` reads perf capability and programs counter/filter offsets. Device setup uses table offsets and WQ/group register layouts to write hardware configuration.

State and persistence: the file describes persistent hardware state in BAR0 and table-backed configuration blocks. WQ/group configuration fields persist until reset/reconfiguration; command status persists until read/cleared; software error and event-log status are hardware-owned until acknowledged; perfmon registers persist until reset. The C unions make bitfield interpretation explicit but inherit all C bitfield layout assumptions already used by the kernel on this target.

Dependencies and integration: includes `uapi/linux/idxd.h` or `linux/idxd.h` for opcode/completion definitions. Integrated with IDXD init, device command, sysfs, perfmon, IRQ, cdev, and DMAengine paths. It also encodes naming compatibility for deprecated token/read-buffer attributes through comments and field aliases consumed by sysfs.

Risks and test signals: register layout errors can misconfigure hardware or mis-handle faults. Risks include version-specific fields, IAA versus DSA capability differences, `WQCFG_OFFSET()`/`GRP*CFG_OFFSET()` arithmetic, EVL entry size differences between DSA and IAX, and command status interpretation. Test on each supported PCI ID/version, validate sysfs capability values against hardware docs, exercise command errors, WQ/group programming, EVL faults, perfmon counters, SWERR ack, and DSA v3 capability exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/submit.c -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/submit.c

Purpose: provides the descriptor allocation, freeing, ENQCMDS retry, and descriptor submission path for kernel IDXD WQs. It is the core bridge from prepared DSA hardware descriptors to the workqueue portal, including active-reference gating and interrupt-completion list registration.

Important APIs and functions: exported namespace symbols are `idxd_alloc_desc()`, `idxd_free_desc()`, and `idxd_submit_desc()`. `idxd_enqcmds()` is shared internally for shared-WQ submission retries. Helpers include `__get_desc()`, `llist_abort_desc()`, and `list_abort_desc()`. The code uses `struct idxd_desc`, `struct idxd_wq`, `struct idxd_irq_entry`, `sbitmap_queue`, `percpu_ref`, and `dsa_hw_desc`.

Control flow: allocation first rejects disabled devices, obtains a descriptor index from the WQ sbitmap, and either returns immediately for nonblocking allocation failure or sleeps interruptibly on the bitmap wait state until a descriptor becomes available. `__get_desc()` clears hardware descriptor and completion record memory, records CPU index, and stamps a device PASID when enabled. Submission verifies device enabled, obtains a live WQ active reference, waits for WQ resurrection if a revoke path killed the ref, stores the interrupt handle and appends the descriptor to `pending_llist` when `IDXD_OP_FLAG_RCI` is set, issues a write memory barrier, and sends through either `iosubmit_cmds512()` for dedicated WQs or `idxd_enqcmds()` for shared WQs. ENQCMDS failure releases the active ref and aborts the pending interrupt descriptor so the completion path cannot retain it indefinitely.

State and persistence: descriptor availability is persisted in `wq->sbq`; descriptor CPU ownership is stored in `desc->cpu`; completion records and hardware descriptors are zeroed per allocation. Active WQ lifetime is coordinated through `wq->wq_active`, `wq_dead`, and `wq_resurrect`, which interact with interrupt-handle revocation in `irq.c`. Pending interrupt descriptors persist in lockless lists until the threaded IRQ consumes or aborts them.

Dependencies and integration: depends on architecture IDXD submission instructions (`enqcmds`, `iosubmit_cmds512`), WQ portal mapping, PASID setup, descriptor completion helpers, and `irq.c` pending-list handling. DMAengine code calls this after preparing operations, while revoke and abort flows in `irq.c` depend on the pending-list invariants established here.

Risks and test signals: key risks are races between submission and interrupt-handle revoke, descriptor reuse after abort, sleeping allocation interruption returning `-EAGAIN`, ENQCMDS retry tuning, and correct ordering of descriptor writes before device doorbell. Test dedicated/shared WQs, blocking and nonblocking allocation exhaustion, signals during allocation wait, disabled device submission, WQ active-ref kill/revive, ENQCMDS busy failure, RCI and non-RCI descriptors, and descriptor completion under concurrent submitters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/submit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/dma/idxd/sysfs.c

Purpose: implements the IDXD configuration and reporting sysfs ABI for device, engine, group, and workqueue configuration devices. It exposes hardware capabilities, state, software errors, cdev numbering, event-log size, group resource allocation, WQ operating parameters, and dynamic child device registration.

Important APIs, types, and functions: exported device types are `idxd_engine_device_type`, `idxd_group_device_type`, `idxd_wq_device_type`, `dsa_device_type`, and `iax_device_type`. Public registration helpers are `idxd_register_devices()` and `idxd_unregister_devices()`. Attribute handlers cover engine `group_id`; group work queue/engine membership, read-buffer allocation, traffic classes, and progress limits; WQ clients/state/group/mode/size/priority/block-on-fault/threshold/type/name/cdev/minor/max transfer/max batch/ATS/PRS/occupancy/ENQCMDS retries/op config/driver name; and device-wide version/capabilities/state/errors/resource limits/command status/event-log size/DSA or IAA caps.

Control flow: store paths parse user input, validate capability and state constraints, then update in-memory configuration. Most mutable attributes require `IDXD_FLAG_CONFIGURABLE` and reject enabled devices or enabled WQs. Group read-buffer accounting recomputes remaining free buffers; WQ size checks aggregate claimed WQ size; WQ op-config parses a 256-bit bitmap and verifies it against device OPCAP. Attribute visibility is dynamic: unsupported progress limits, IAA-incompatible read-buffer fields, missing WQ capabilities, IAA batch limits, IAA-only caps, EVL support, and DSA v3 caps are hidden. Registration adds parent device first, then WQ, engine, and group devices with staged cleanup on failure.

State and persistence: sysfs writes mutate persistent driver configuration in `idxd_device`, `idxd_group`, `idxd_engine`, and `idxd_wq` objects. These values later drive hardware configuration and WQ enablement. Release callbacks free WQ opcap bitmaps/config arrays/xarrays, group/engine structures, event-log memory/cache, workqueue, device IDA allocation, WQ enable bitmap, and device-level opcap bitmap. `cmd_status_store()` clears saved command status.

Dependencies and integration: depends on Linux device core, sysfs helpers, IDXD configuration object conversions, capability bits from `registers.h`, cdev state, xarray PASID state, and init/device code that allocates child objects before registration. `submit.c` reads `enqcmds_retries`; `irq.c` updates software error state shown here.

Risks and test signals: risks include ABI regressions, missing state guards allowing live hardware reconfiguration, group resource underflow/overflow, bitmap parse mistakes, and cleanup ordering after partial registration failure. Test by enumerating sysfs for DSA and IAA devices across versions, writing every mutable attribute in enabled and disabled states, verifying invisible unsupported attributes, configuring WQs/groups then enabling hardware, checking deprecated token aliases, reading SWERR after injected errors, resizing EVL within bounds, and module remove after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/idxd/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/img-mdc-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/img-mdc-dma.c

Purpose: implements the Imagination Technologies Multi-threaded DMA Controller platform driver, using the virt-dma framework to support memcpy, slave scatter-gather, and cyclic DMA on Pistachio-style SoCs. It builds hardware linked-list descriptors, routes peripheral requests through syscon registers, manages per-channel interrupts, and integrates runtime/system power management.

Important APIs, types, and functions: core types are `struct mdc_dma`, `struct mdc_chan`, `struct mdc_tx_desc`, and `struct mdc_hw_list_desc`. DMAengine callbacks include `mdc_prep_dma_memcpy()`, `mdc_prep_slave_sg()`, `mdc_prep_dma_cyclic()`, `mdc_issue_pending()`, `mdc_tx_status()`, `mdc_terminate_all()`, `mdc_synchronize()`, `mdc_slave_config()`, `mdc_alloc_chan_resources()`, and `mdc_free_chan_resources()`. IRQ and OF integration are handled by `mdc_chan_irq()` and `mdc_of_xlate()`.

Control flow: probe maps registers, obtains the peripheral syscon and clock, reads global hardware configuration, creates a DMA descriptor pool, initializes channels and per-channel IRQs, registers DMAengine and OF DMA provider, and enables runtime PM. Prep functions allocate one or more pool descriptors capped at `max_xfer_size`, link them by physical `node_addr`, set transfer width/increment/DREQ/burst fields, and return virt-dma descriptors. Issue enables SoC request routing, writes the first list address, and starts list mode. The IRQ handler acknowledges new hardware command events, treats the first event as command-list loaded, advances `list_cmds_done`, fires cyclic period callbacks, completes non-cyclic cookies, and immediately issues the next queued descriptor.

State and persistence: persistent state includes channel active descriptor, slave configuration, peripheral/thread routing, descriptor pool allocations, runtime clock state, hardware command counters, and SoC route registers. Residue calculation reads stable snapshots of `MDC_CMDS_PROCESSED` and `MDC_ACTIVE_TRANSFER_SIZE`. Cyclic descriptors stay active and wrap their linked list.

Dependencies and integration: depends on platform resources, device tree `img,pistachio-mdc-dma`, `img,cr-periph`, `dma-channels`, and `img,max-burst-multiplier`, the common clock framework, regmap/syscon, OF DMA translation with three cells, DMAengine, and virt-dma tasklet cleanup.

Risks and test signals: risks include ambiguous maximum transfer residue, list event accounting off by one, IRQs without active descriptors, missing route disable, cyclic wrap/period math, and suspend while channels are active. Test memcpy splitting, slave SG in both directions, cyclic audio-style periods, residue queries during transfer, terminate/synchronize, runtime PM clock balance, DT channel/thread routing, suspend-late `-EBUSY`, and probe/remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/img-mdc-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/imx-dma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/imx-dma.c

Purpose: implements the legacy Freescale i.MX1/i.MX21/i.MX27 DMAengine driver. It supports slave SG, cyclic, memcpy, and interleaved 2D transfers over a 16-channel DMA controller with register programming, tasklet-driven completions, optional i.MX27 hardware chaining, and OF DMA request translation.

Important APIs, types, and functions: core types are `struct imxdma_engine`, `struct imxdma_channel`, `struct imxdma_desc`, and `struct imx_dma_2d_config`. DMAengine callbacks include `imxdma_alloc_chan_resources()`, `imxdma_free_chan_resources()`, `imxdma_prep_slave_sg()`, `imxdma_prep_dma_cyclic()`, `imxdma_prep_dma_memcpy()`, `imxdma_prep_dma_interleaved()`, `imxdma_config()`, `imxdma_tx_status()`, `imxdma_terminate_all()`, and `imxdma_issue_pending()`. Interrupt paths are `dma_irq_handler()`, `imxdma_err_handler()`, `dma_irq_handle_channel()`, and `imxdma_tasklet()`.

Control flow: probe enables IPG/AHB clocks, resets/enables the controller, clears/masks interrupts, requests shared or per-channel IRQs depending on SoC type, initializes channel descriptor lists, registers DMAengine, and optionally registers an OF DMA controller. Resource allocation preallocates up to 16 descriptors per channel. Prep functions fill the first free descriptor but leave it on `ld_free` until `tx_submit()` moves it to `ld_queue`. `issue_pending()` programs the first queued descriptor and moves it active. IRQ handling advances SG segments, restarts chained transfers or disables the channel, then schedules a tasklet. The tasklet completes non-cyclic cookies, frees 2D slots, recycles descriptors, starts the next queued descriptor, and invokes callbacks; cyclic descriptors stay active and callback on each period progression.

State and persistence: per-channel state includes free/queued/active descriptor lists, DMA request line, slave config, watermark, bus width, 2D slot ownership, hardware chaining flag, watchdog timer, and cyclic SG list. Engine-global state includes two reusable 2D slots, clocks, register base, and lock. Hardware register state is programmed per transfer and cleared on termination/free.

Dependencies and integration: depends on `linux/dma/imx-dma.h` filter data, OF compatibles `fsl,imx1-dma` and `fsl,imx27-dma`, clock names `ipg` and `ahb`, DMAengine core, legacy tasklets, and platform IRQ layout. Clients may use OF xlate with one request cell or legacy `chan->private` filter data.

Risks and test signals: risks include list handling because descriptors remain on `ld_free` until submit, SG alignment validation only checking first entry, cyclic self-chained SG allocation, tasklet callback on error paths, watchdog timing for hardware chaining, and cleanup using disabled IRQs/tasklets. Test all transfer modes, i.MX1 shared IRQ and i.MX27 per-channel IRQs, error status registers, 2D slot contention, cyclic terminate/free, DMA request selection, clock unwind on probe errors, and max segment boundary handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/imx-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/imx-sdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/imx-sdma.c

Purpose: implements the Freescale/NXP Smart DMA platform driver for many i.MX SoCs. Unlike simple DMA controllers, SDMA contains a programmable DMA processor; this driver initializes channel-control memory, loads ROM or external firmware script addresses, programs channel contexts through channel 0, prepares buffer descriptors, and exposes DMAengine slave, cyclic, memcpy, and device-to-device flows.

Important APIs, types, and functions: major structures are `sdma_engine`, `sdma_channel`, `sdma_desc`, `sdma_buffer_descriptor`, `sdma_channel_control`, `sdma_context_data`, `sdma_script_start_addrs`, and `sdma_driver_data`. DMAengine callbacks include `sdma_alloc_chan_resources()`, `sdma_free_chan_resources()`, `sdma_prep_memcpy()`, `sdma_prep_slave_sg()`, `sdma_prep_dma_cyclic()`, `sdma_config()`, `sdma_tx_status()`, `sdma_issue_pending()`, `sdma_terminate_all()`, and `sdma_channel_synchronize()`. Initialization and firmware flow use `sdma_init()`, `sdma_request_channel0()`, `sdma_load_script()`, `sdma_load_firmware()`, `sdma_add_scripts()`, and `sdma_event_remap()`.

Control flow: probe coerces 32-bit DMA masks, maps registers, prepares clocks, requests the main IRQ, allocates script address storage, initializes all virt-dma channels except internal channel 0, optionally obtains IRAM, initializes SDMA control/context memory, remaps events through GPR syscon, seeds SoC ROM script addresses, registers DMAengine and OF DMA provider, and asynchronously requests optional firmware named by DT. Channel allocation sets priority and event IDs. Configuration enables SDMA events early, records FIFO/peripheral metadata, calculates event masks/watermarks, chooses a script PC for the peripheral type/direction, and loads the channel context via channel 0. Prep functions allocate coherent or IRAM BDs, fill count/command/status fields, and set loop flags for cyclic transfers. IRQ handling acknowledges completed channels, updates cyclic BDs and invokes callbacks in interrupt context, or completes normal descriptors and starts the next queued descriptor.

State and persistence: persistent state spans hardware channel priorities, event enable registers, channel ownership override registers, script address tables, firmware-loaded flag, channel contexts in coherent memory, current active descriptor, terminated descriptor list, clocks enabled per allocated channel, and optional IRAM allocations. Cyclic residue uses `buf_tail`, `buf_ptail`, period length, and real hardware counts. Termination defers freeing the current descriptor through workqueue delay to allow the SDMA core to stop.

Dependencies and integration: depends on OF compatibles for i.MX25/31/35/51/53/6q/6ul/7d/8mq, optional `iram`, `gpr`, `fsl,sdma-event-remap`, and `fsl,sdma-ram-script-name` properties, NXP firmware files, common clock, genalloc, regmap/syscon, DMAengine/virt-dma, and `linux/dma/imx-dma.h` peripheral type data. Some scripts require external RAM firmware; ROM script fallbacks are SoC-specific.

Risks and test signals: risks include firmware/header validation and asynchronous load timing, RAM-script transfers before firmware is ready, channel 0 serialization, event enable ordering, peripheral-specific script selection, p2p watermark bit packing, cyclic callback/restart races, BD count limits, and remove calling free on channel 0 style objects. Test DT xlate, each SoC script table, missing and valid firmware, memcpy, slave SG, cyclic, HDMI special cyclic path, P2P ASRC, SAI FIFO config, terminate/synchronize, residue during cyclic and normal transfers, event remap, IRAM allocation, and clock balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/imx-sdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/Makefile -->
# sources/distributed-fs/ceph-client/drivers/dma/ioat/Makefile

Purpose: declares how the Intel I/OAT DMA driver objects are built under Kbuild. When `CONFIG_INTEL_IOATDMA` is enabled, it builds one composite module/object named `ioatdma.o` from initialization, DMA engine, prep, DCA, and sysfs implementation files.

Important APIs and entries: `obj-$(CONFIG_INTEL_IOATDMA) += ioatdma.o` connects the driver to the kernel configuration symbol. `ioatdma-y := init.o dma.o prep.o dca.o sysfs.o` lists the mandatory object files linked into the composite target. There are no optional per-feature object fragments in this Makefile; DCA support code is compiled into the I/OAT object, while runtime/module parameters and platform checks decide whether DCA is registered.

Control flow: Kbuild evaluates this file during kernel build. If the config symbol is built-in, all listed objects are linked into vmlinux through the driver subtree; if modular, they become the `ioatdma` module. Link order places `init.o` before operational components, but runtime entry points are driven by module init/PCI driver registration in `init.c`.

State and persistence: no runtime state exists in the Makefile. Its persistent effect is build composition: changes alter which code is present in the driver binary and therefore which symbols are available to `init.c`, `dma.c`, `prep.c`, `dca.c`, and `sysfs.c`.

Dependencies and integration: depends on the parent DMA Kbuild including this directory and on Kconfig defining `CONFIG_INTEL_IOATDMA`. The linked object list corresponds to internal headers such as `dma.h`, `hw.h`, and `registers.h`; removing any listed object would leave unresolved driver functionality.

Risks and test signals: risks are build-only: stale object lists, missing optional guards, or file renames break compilation or silently omit functionality. Test `make drivers/dma/ioat/`, built-in and module configurations for `CONFIG_INTEL_IOATDMA`, `modinfo ioatdma`, and link errors after changing IOAT source file boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/dca.c -->
# sources/distributed-fs/ceph-client/drivers/dma/ioat/dca.c

Purpose: implements Direct Cache Access provider support for Intel I/OAT DMA devices. It verifies CPU/BIOS DCA enablement, discovers I/OAT DCA requester slots, registers a `dca_provider`, maps requester PCI IDs into hardware tables, and converts CPU APIC IDs into DCA tags using a BIOS-provided tag map.

Important APIs, types, and functions: public functions are `system_has_dca_enabled()` and `ioat_dca_init()`. DCA provider operations are `ioat_dca_add_requester()`, `ioat_dca_remove_requester()`, `ioat_dca_get_tag()`, and `ioat_dca_dev_managed()`. State lives in `struct ioat_dca_priv`, which contains MMIO bases, requester count/capacity, tag map bytes, and flexible `ioat_dca_slot` entries containing requester PCI devices and requester IDs.

Control flow: `system_has_dca_enabled()` checks the boot CPU DCA feature and CPUID leaf 9 BIOS-enable bit. `ioat_dca_init()` then reads the device DCA offset, counts global requester table slots until `IOAT_DCA_GREQID_LASTID`, allocates a provider with enough private slot storage, enables prefetch/memory-write DCA controls if BIOS left them off, reads the APIC-ID tag map, masks unsupported bits, rejects a known invalid default map with firmware taint, and registers the provider. Adding a requester requires a PCI device, finds a free slot, records the device and requester ID, and writes `IOAT_DCA_GREQID_VALID` into the global requester table. Removing a requester clears the hardware table slot and local bookkeeping. Tag calculation walks eight tag map entries and selects, inverts, or literals bits into the returned tag.

State and persistence: provider state persists while the IOAT device is registered and is freed by `init.c` remove paths through `unregister_dca_provider()`/`free_dca_provider()`. Hardware requester table entries persist until removed or device reset. The tag map is snapshotted at provider initialization; later BIOS or firmware changes are not re-read.

Dependencies and integration: depends on x86 CPUID/APIC ID helpers, PCI device IDs, Linux DCA core, IOAT register definitions, and IOAT probe/remove code in `init.c`. The Makefile always links this object into `ioatdma`, but initialization only happens if module/runtime DCA settings and hardware checks pass.

Risks and test signals: risks include BIOS-disabled or misprogrammed DCA, non-PCI requesters, requester slot exhaustion, incorrect tag maps on CPU topology changes, and MMIO table offset assumptions. Test on DCA-capable x86 systems with BIOS DCA on/off, invalid tag map firmware, adding/removing multiple requester devices, slot exhaustion, CPU hotplug or APIC-ID variation, IOAT remove cleanup, and DMA clients that request DCA tags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/ioat/dca.c -->
