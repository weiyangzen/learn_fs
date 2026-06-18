# Research Report: subset-b-004269

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/alcor.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/alcor.c

## Purpose
`alcor.c` is a Linux MMC host driver for Alcor Micro AU6601/AU6621 PCI-attached SD card controller functions. It is explicitly reverse-engineered from observed hardware behavior and a vendor driver rather than public documentation, so much of the register programming is conservative and sequence-sensitive. The driver exposes the controller through `struct mmc_host_ops` and depends on the companion Alcor PCI core for MMIO helpers and register definitions.

## Important APIs, Types, and Functions
The central state object is `struct alcor_sdmmc_host`, which stores the active `mmc_request`, command/data pointers, DMA/PIO scatterlist state, delayed timeout work, IRQ status, current power mode, and a `cmd_mutex` serializing request, IRQ-thread, timeout, and IOS paths. `enum alcor_cookie` records whether MMC core pre-request DMA mapping was skipped, pre-mapped, or mapped.

Key operations are `alcor_request`, `alcor_pre_req`, `alcor_post_req`, `alcor_set_ios`, `alcor_get_cd`, `alcor_get_ro`, `alcor_card_busy`, and `alcor_signal_voltage_switch`, wired into `alcor_sdc_ops`. Transfer helpers include `alcor_send_cmd`, `alcor_prepare_data`, `alcor_trigger_data_transfer`, `alcor_trf_block_pio`, `alcor_data_set_dma`, `alcor_finish_data`, and `alcor_request_complete`. Probe/remove/PM are handled by `alcor_pci_sdmmc_drv_probe`, `alcor_pci_sdmmc_drv_remove`, `alcor_pci_sdmmc_suspend`, and `alcor_pci_sdmmc_resume`.

## Control Flow and State
Probe allocates an MMC host, disables controller interrupts, requests a shared threaded IRQ, initializes the mutex and timeout work, configures MMC limits/capabilities, and performs hardware init. Requests enter `alcor_request`, are rejected with `-ENOMEDIUM` if card-detect is false, otherwise `alcor_send_cmd` writes opcode/argument/response control and arms a delayed timeout. Command completion can be handled in the hard IRQ fast path when all needed work is simple; otherwise the IRQ masks SD interrupts, records status, and wakes `alcor_irq_thread`.

Data transfers are PIO by default or page-at-a-time DMA for large aligned CMD18/CMD25 transfers. DMA is only selected in `pre_req` when every segment is 4096 bytes, segment offsets are zero, block size is word-aligned, and the request is large enough. The hardware cannot scatter-gather directly, so each DMA-end interrupt advances to the next page with `alcor_data_set_dma`. PIO uses `sg_mapping_iter` and transfers one block per buffer-ready interrupt. `alcor_finish_data` sends CMD12 for open-ended or failed multiblock transfers, otherwise completes the request.

## State and Persistence Behavior
The driver persists only volatile kernel and hardware state: current request pointers, SG iterators, cached power mode, IRQ snapshot, and controller registers. No durable data is stored by this file. Power sequencing and hardware initialization write multiple unexplained registers, reset command/data engines, set pins to input, configure card detect, and later uninitialize by masking IRQs, resetting engines, powering off VDD, and clearing voltage options.

## Dependencies and Integration Points
This file integrates with Linux MMC core, DMA mapping, scatterlist iteration, platform-driver binding via `DRV_NAME_ALCOR_PCI_SDMMC`, delayed work, threaded IRQs, and Alcor PCI helpers from `<linux/alcor_pci.h>`. It advertises SD high-speed and UHS modes, 4-bit data, no SDIO, a 3.3 V OCR, and request/segment limits matching hardware and vendor-driver behavior.

## Risks and Test Signals
Risks are concentrated around undocumented register sequences, interrupt masking losing status updates, strict DMA assumptions, the 240-sector request cap, timeout race handling, and card removal during active requests. Test signals include successful probe and `mmc_add_host`, card insertion/removal detection, PIO and DMA reads/writes across aligned and unaligned SG layouts, multiblock stop handling, voltage switch behavior, suspend/resume, timeout recovery, and absence of leaked DMA mappings after `post_req`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/alcor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/atmel-mci.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/atmel-mci.c

## Purpose
`atmel-mci.c` implements the Atmel/AT91 Multimedia Card Interface and High-Speed MCI host driver. It supports up to two logical MMC slots sharing one controller, multiple hardware generations, PIO/PDC/DMA transfer engines, GPIO card-detect/write-protect, SDIO IRQs, debugfs inspection, and runtime power management.

## Important APIs, Types, and Functions
Important state types are `struct atmel_mci` for controller-wide state, `struct atmel_mci_slot` for per-slot MMC state, `struct atmel_mci_caps` for version-derived quirks, `struct atmel_mci_dma` for DMAengine state, and `enum atmel_mci_state` for the bottom-half state machine. Public MMC callbacks are `atmci_request`, `atmci_set_ios`, `atmci_get_ro`, `atmci_get_cd`, and `atmci_enable_sdio_irq` via `atmci_ops`.

Core functions include `atmci_of_init`, `atmci_get_cap`, `atmci_prepare_command`, `atmci_start_request`, `atmci_work_func`, `atmci_interrupt`, `atmci_read_data_pio`, `atmci_write_data_pio`, `atmci_prepare_data`, `atmci_prepare_data_pdc`, `atmci_prepare_data_dma`, `atmci_dma_complete`, `atmci_pdc_complete`, `atmci_request_end`, `atmci_detect_change`, `atmci_init_slot`, `atmci_configure_dma`, `atmci_probe`, and runtime PM callbacks.

## Control Flow and State
Device tree child nodes describe slots. Probe maps registers, enables `mci_clk`, resets the controller, requests the main IRQ, detects controller capabilities from `ATMCI_VERSION`, selects DMA/PDC/PIO function pointers, initializes runtime PM, and creates slot MMC hosts. Each request is queued per slot under `host->lock`; if idle, `atmci_start_request` selects the slot, optionally resets the controller, applies slot bus selection, programs timeouts/block registers, prepares data, sends the command, starts the transfer engine, and enables interrupts.

Interrupts do minimal status capture and event setting. The state machine in `atmci_work_func` consumes `EVENT_CMD_RDY`, `EVENT_XFER_COMPLETE`, `EVENT_NOTBUSY`, and `EVENT_DATA_ERROR` while moving through `STATE_SENDING_CMD`, `STATE_DATA_XFER`, `STATE_WAITING_NOTBUSY`, `STATE_SENDING_STOP`, and `STATE_END_REQUEST`. It performs response decoding, data completion, stop-command sequencing, and queue advancement. PDC mode double-buffers through PDC registers; DMA mode uses a `rxtx` DMAengine channel and waits for NOTBUSY after completion; PIO mode drains/fills RDR/TDR on RXRDY/TXRDY.

## State and Persistence Behavior
Persistent state is in-memory and hardware-register only: queued slots, active request pointers, pending/completed event bitmaps, cached mode/config registers, slot clocks, card-present flags, runtime PM clock state, debugfs views, and an optional coherent bounce buffer for old controllers without read/write proof. No filesystem or durable media state is written. Card-detect timers debounce GPIO IRQs and cancel/complete active or queued requests with `-ENOMEDIUM` when cards disappear.

## Dependencies and Integration Points
The driver integrates with MMC core, OF child slot bindings, GPIO descriptor APIs, regulators, debugfs, DMAengine, Atmel PDC definitions, pinctrl PM states, timers/workqueues, and platform-driver PM. Version capability gates determine high-speed support, odd clock divider support, config/CSTOR registers, PDC availability, DMA handshaking, read/write proof, data-ordering workarounds, reset-after-transfer quirks, and block-size constraints.

## Risks and Test Signals
Risks include races between IRQ status capture and workqueue state transitions, shared-controller multi-slot clock changes, older hardware data ordering and non-word-size errata, DMA/PDC cleanup on timeout/removal, GPIO detect polarity, and runtime PM while debugfs snapshots registers. Test signals should cover probe with one and two slots, PIO/PDC/DMA fallback, small and non-word-aligned transfers, multiblock stop handling, SDIO IRQ routing, card removal during queued and active requests, runtime suspend/resume, debugfs `regs`/`req`, and DMA channel defer/failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/atmel-mci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/au1xmmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/au1xmmc.c

## Purpose
`au1xmmc.c` is the MMC/SD/SDIO host driver for Alchemy Au1xxx SoCs. It supports platform-data based card power, detect, read-only callbacks, optional DBDMA on supported CPUs, PIO fallback, shared IRQ handling, basic suspend/resume, and optional LED trigger registration.

## Important APIs, Types, and Functions
`struct au1xmmc_host` tracks the `mmc_host`, active request, MMIO base, clock/bus/power state, status enum-like values, DMA and PIO cursors, DBDMA channel IDs, work items, platform data, IRQ, resource, and clock. MMC callbacks are `au1xmmc_request`, `au1xmmc_set_ios`, `au1xmmc_card_readonly`, `au1xmmc_card_inserted`, and `au1xmmc_enable_sdio_irq`. Important helpers include `au1xmmc_send_command`, `au1xmmc_prepare_data`, `au1xmmc_cmd_complete`, `au1xmmc_data_complete`, PIO send/receive helpers, `au1xmmc_irq`, DBDMA init/shutdown/callback, and probe/remove/PM functions.

## Control Flow and State
Probe allocates a devm MMC host but manually requests/remaps MMIO, requests the IRQ, gets/enables the Alchemy peripheral clock, configures caps based on CPU type, sets up card-detect platform hooks, initializes work items, optionally allocates DBDMA channels, resets the controller, and calls `mmc_add_host`. A request starts only from `HOST_S_IDLE`, rejects absent cards, flushes FIFO for data, maps SG data, sets DBDMA descriptors or enables PIO FIFO interrupts, then writes command argument and command bits. The IRQ handles SDIO, timeouts, command complete, PIO FIFO readiness, and schedules bottom-half work for completion.

## State and Persistence Behavior
The host keeps volatile status flags such as `HOST_F_XMIT`, `HOST_F_RECV`, `HOST_F_DMA`, `HOST_F_DBDMA`, `HOST_F_STOP`, and controller states `HOST_S_IDLE/CMD/DATA/STOP`. DMA mappings are released in `au1xmmc_data_complete`; PIO cursors are reset in `au1xmmc_finish_request`. No durable persistence exists. Hardware state is reset by programming enable/status/config/timeout registers and by flushing FIFOs around requests and resume.

## Dependencies and Integration Points
This driver depends on MIPS Alchemy headers, platform data from `au1100_mmc.h`, DBDMA APIs, Linux MMC core, clock APIs, workqueues, IRQs, scatterlist DMA mapping, highmem page mapping for PIO, and optional LED class support. It registers as platform driver `au1xxx-mmc` and uses CPU model detection to set max segment size, f_max, 8-bit support, IRQ sharing, and DBDMA availability.

## Risks and Test Signals
Risks include busy-wait command submission without an explicit timeout, hand-coded DBDMA descriptor setup, platform-data card detect returning `-ENOSYS`, shared IRQ behavior, timeout/error cleanup in PIO with interrupts still enabled, and manual resource cleanup despite partial devm use. Test signals include PIO and DBDMA reads/writes, command response decoding including 136-bit shifts, card absence, SDIO IRQ enable, platform power hooks, Au1100/Au1200/Au1300 CPU capability differences, suspend/resume reset, and probe failure unwind with IRQ/MMIO/clock resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/au1xmmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/bcm2835.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/bcm2835.c

## Purpose
`bcm2835.c` implements the Raspberry Pi BCM2835 custom SDHost controller driver. It targets the non-SDHCI SD card controller, leaving the Arasan SDHCI controller available for SDIO/Wi-Fi on platforms such as Raspberry Pi 3. It supports PIO, optional DMAengine transfers, command busy handling, CMD23, hardware reset, polling card-detect behavior, and platform/OF probing.

## Important APIs, Types, and Functions
`struct bcm2835_host` contains MMIO/physical addresses, clock and cached config/divider registers, IRQ and locking primitives, current request/command/data, PIO SG iterator and block count, threaded IRQ flags, timeout/dma work, DMA channel/config/descriptor state, and the read-drain workaround fields. MMC callbacks are `bcm2835_request`, `bcm2835_set_ios`, and `bcm2835_reset` via `bcm2835_ops`. Important helpers include `bcm2835_send_command`, `bcm2835_finish_command`, `bcm2835_finish_data`, `bcm2835_transfer_complete`, `bcm2835_prepare_dma`, `bcm2835_transfer_pio`, hard/threaded IRQ handlers, `bcm2835_dma_complete_work`, `bcm2835_set_clock`, `bcm2835_add_host`, and probe/remove/PM callbacks.

## Control Flow and State
Probe allocates an MMC host, maps MMIO, extracts the physical register address for DMA, requests an optional `rx-tx` DMA channel, parses MMC OF properties, enables the clock, and initializes host capabilities. Requests validate block size power-of-two constraints, serialize under `host->mutex`, verify the controller FSM is idle, prepare DMA for transfers larger than `PIO_THRESHOLD`, optionally send CMD23 for reads, send the actual command, start DMA if prepared, and poll immediate command completion when no busy response is expected.

The hard IRQ records block, busy, and data conditions under a spinlock and wakes the threaded IRQ. The threaded handler serializes with request code via the mutex and invokes block, busy, and data handlers. PIO uses the controller FIFO occupancy in SDEDM and an SG iterator; DMA uses DMAengine callbacks and a work item because completion must not finalize the request directly in DMA callback context. For multi-block DMA reads, final words are drained manually from FIFO due to a DREQ/FIFO hardware issue.

## State and Persistence Behavior
State is volatile: cached `hcfg/cdiv`, current request pointers, `data_complete`, `use_busy`, `use_sbc`, DMA descriptors, delayed timeout work, and PIO/DMA transfer cursors. Reset powers the card off/on, clears command/status/block registers, sets FIFO thresholds, restores cached config/divider, and marks current clock zero. No durable state is persisted.

## Dependencies and Integration Points
The driver uses MMC core, OF address parsing, platform resources, Linux clk, DMAengine, scatterlist mapping, highmem local mapping, threaded IRQs, delayed work, and the `brcm,bcm2835-sdhost` compatible string. It advertises high-speed SD/MMC, command queue limits, CMD23, hardware reset, polling detect, 3.2-3.4 V OCR, and fallback to PIO when DMA setup is unavailable.

## Risks and Test Signals
Risks include undocumented FIFO/FSM behavior, forced slow-card clocking for high core clocks, DMA SG mutation for read drain words, races between command and data completion, timeout reset paths, and PIO timeouts in tight loops. Test signals include DMA and PIO transfers, single and multiblock reads/writes, CMD23 read sequencing, stop command after errors/open-ended transfers, long busy timeouts, block-size rejection, DMA probe defer/fallback, suspend/resume clock handling, and remove-time cancellation of work and IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/bcm2835.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cavium-octeon.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/cavium-octeon.c

## Purpose
`cavium-octeon.c` is the OCTEON platform front end for the shared Cavium MMC/eMMC host implementation in `cavium.c`/`cavium.h`. It binds OF platform devices, maps OCTEON register windows, wires interrupt registration, bus serialization, shared power GPIO handling, and model-specific DMA corruption workarounds.

## Important APIs, Types, and Functions
The file populates `struct cvm_mmc_host` callbacks: `octeon_mmc_acquire_bus`, `octeon_mmc_release_bus`, `octeon_mmc_int_enable`, `octeon_mmc_set_shared_power`, `octeon_mmc_dmar_fixup`, and `octeon_mmc_dmar_fixup_done`. Probe and remove are `octeon_mmc_probe` and `octeon_mmc_remove`. Low-level L2 cache helpers `phys_to_ptr`, `l2c_lock_line`, `l2c_unlock_line`, `l2c_lock_mem_region`, and `l2c_unlock_mem_region` implement the EMMC-17978 workaround on affected CN6XXX/CNF7XXX models.

## Control Flow and State
Probe allocates a common host, initializes the IRQ handler spinlock and serializer semaphore, assigns common callbacks, sets optional DMA fixup callbacks for affected models, records the IO clock rate, detects CIU3/big-DMA/SG capability for `cavium,octeon-7890-mmc`, maps control and DMA resources, sets a 64-bit DMA mask, clears bootloader-left interrupts, requests either per-bit CIU3 IRQs or a legacy IRQ, acquires optional global power GPIO, and creates one platform child per slot before calling `cvm_mmc_of_slot_probe`.

Removal removes all slot hosts, disables DMA engine enable in `MIO_EMM_DMA_CFG`, and drops shared power. Bus acquisition serializes access either with `octeon_bootbus_sem` plus a CN70XX boot-bus mux write or with the host semaphore for CIU3 systems.

## State and Persistence Behavior
State is volatile in `cvm_mmc_host`: callback pointers, mapped register bases, register offsets, feature flags, slot devices, global power user count, and `n_minus_one` L2 lock address for the workaround. No persistent files are written. Shared power is reference-counted through `shared_power_users` and a global GPIO.

## Dependencies and Integration Points
The file depends on OF platform devices, OCTEON model/bootbus APIs, GPIO descriptors, DMA mask setup, IRQ type overrides for legacy firmware, and the shared `cvm_mmc_interrupt` plus slot probe/remove APIs. Compatible strings are `cavium,octeon-6130-mmc` and `cavium,octeon-7890-mmc`.

## Risks and Test Signals
Risks include model-specific paths, legacy U-Boot IRQ type workarounds, child slot creation cleanup, shared power reference imbalance, bootbus serialization, and cache-line locking for the DMA workaround. Test signals include probe on legacy and CIU3 OCTEON variants, all IRQ lines firing through `cvm_mmc_interrupt`, multi-slot add/remove, global power on/off across slots, DMA write workload on workaround models, and error unwind after partial slot creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cavium-octeon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cavium-thunderx.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/cavium-thunderx.c

## Purpose
`cavium-thunderx.c` is the PCI front end for the shared Cavium MMC/eMMC core. It supports ThunderX controllers exposed as Cavium PCI device `0xa010`, maps PCI BARs, enables clocks, configures MSI-X interrupts, creates OF slot child devices, and delegates slot-level behavior to `cavium.c`.

## Important APIs, Types, and Functions
Important functions are `thunder_mmc_acquire_bus`, `thunder_mmc_release_bus`, `thunder_mmc_int_enable`, `thunder_mmc_register_interrupts`, `thunder_mmc_probe`, and `thunder_mmc_remove`. They populate `struct cvm_mmc_host` fields such as `base`, `dma_base`, `reg_off`, `reg_off_dma`, `clk`, `sys_freq`, `use_sg`, `big_dma_addr`, `need_irq_handler_lock`, callbacks, slot arrays, and serializer state.

## Control Flow and State
Probe allocates the common host, enables the PCI device with managed PCI helpers, requests BARs, maps BAR0, uses the same base for DMA registers, sets ThunderX-specific register offsets, enables the controller clock, initializes locking, sets DMA mask to 48 bits, clears stale command/DMA interrupts and DMA FIFO state, allocates one to nine MSI-X vectors, and registers each vector against `cvm_mmc_interrupt` with a descriptive shared IRQ-name table. It then iterates OF children compatible with `mmc-slot`, creates a platform child device for each, and calls `cvm_mmc_of_slot_probe`.

Removal tears down all slot MMC hosts, disables DMA, and disables the clock. Error unwind destroys partially created slot devices and disables the clock.

## State and Persistence Behavior
The file stores no durable state. Runtime state is the PCI driver data pointer to `cvm_mmc_host`, the mapped register window, clock enable state, slot platform devices, and the common host’s active request/slot state. Interrupt enable writes are done through `MIO_EMM_INT` and `MIO_EMM_INT_EN_SET`, while stale DMA IRQ state is cleared during probe.

## Dependencies and Integration Points
Dependencies include PCI managed resource APIs, MSI-X allocation, Linux clk, OF child nodes under a PCI device, DMA masks, and the shared Cavium MMC core exported by `cavium.h`. The file registers `module_pci_driver(thunder_mmc_driver)` and depends on the common `cvm_mmc_interrupt`, `cvm_mmc_of_slot_probe`, and `cvm_mmc_of_slot_remove` entry points.

## Risks and Test Signals
Risks include partial MSI-X vector allocation, OF child lifetime handling, clock cleanup on every error path, lack of explicit `pci_free_irq_vectors` in remove/error paths, and shared-core assumptions about ThunderX register offsets. Test signals include PCI probe/remove, MSI-X vector count from 1 to 9, slot child creation, DMA and command IRQ delivery, clock enable/disable, SG DMA requests, and error unwind with partially initialized slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cavium-thunderx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cavium.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/cavium.c

## Purpose
`cavium.c` is the shared MMC/eMMC host implementation used by OCTEON and ThunderX front ends. It translates MMC core requests into Cavium MIO_EMM command, switch, buffer, and external DMA register operations, manages per-slot state on a shared controller, handles common interrupts, and probes/removes logical slot hosts from OF children.

## Important APIs, Types, and Functions
External symbols are `cvm_mmc_irq_names`, `cvm_mmc_interrupt`, `cvm_mmc_of_slot_probe`, and `cvm_mmc_of_slot_remove`. Key internals include `cvm_mmc_get_cr_mods`, `do_switch`, `cvm_mmc_switch_to`, `set_wdog`, `do_read`, `do_write_request`, `set_cmd_response`, `check_status`, `finish_dma`, `prepare_dma_single`, `prepare_dma_sg`, `prepare_ext_dma`, `cvm_mmc_dma_request`, `cvm_mmc_request`, `cvm_mmc_set_ios`, `cvm_mmc_init_lowlevel`, and `cvm_mmc_of_parse`.

## Control Flow and State
Every request acquires the bus through a front-end callback and releases it only on completion interrupt. Multiblock read/write requests are forced down the external DMA path and require a stop command. Single-block or non-data commands use the command path: switch to the target slot, prepare inline buffer data for ADTC writes or start SG iteration for reads, set watchdog, enable command interrupts, compute command/response XOR overrides, wait for stale hardware busy bits to clear, and write `MIO_EMM_CMD`.

The interrupt handler clears interrupt bits, checks switch errors, skips completion while DMA is still active, copies buffer data for non-DMA transfers on `BUF_DONE`, checks command/DMA done/error bits, maps response status into `cmd->error`, finishes DMA and unmaps SG, decodes responses, cleans pending DMA on error, clears `current_req`, calls `req->done`, invokes any DMA erratum completion hook, and releases the shared bus.

## State and Persistence Behavior
State is maintained in `struct cvm_mmc_host` and `struct cvm_mmc_slot`: current request, active DMA flag, SG iterator, cached per-slot switch/RCA values, slot clock, bus id, sample delay counts, feature flags, and callback pointers. No durable persistence exists. Slot switching saves the old slot’s switch/RCA registers and restores the new slot’s cached registers/sample delays. IOS updates control power through either a global GPIO callback or regulator, reset bus on power-off, and program clock, width, timing, and power class fields.

## Dependencies and Integration Points
The shared core depends on Linux MMC, OF properties, regulators, MMC GPIO helpers, DMA mapping, scatterlist iteration, bitfield macros, and front-end callbacks for bus locking, interrupt enabling, DMA fixups, and shared power. It consumes common properties via `mmc_of_parse`, legacy `cavium,bus-max-width`, `spi-max-frequency`, and Cavium skew properties. It advertises high-speed MMC/SD, CMD23, power-off-card, 3.3 V DDR, max block/count limits, and max SG count based on front-end SG capability.

## Risks and Test Signals
Risks include strict DMA requirements for multiblock requests, maximum SG FIFO count of 16, 8-byte DMA alignment/size assumptions, shared-controller slot switching, front-end bus-release correctness, response type XOR table correctness for SD vs MMC commands, and cleanup when DMA errors leave `DMA_PEND` set. Test signals include command-only requests, inline data requests, multiblock DMA reads/writes, SD and MMC response types, slot switching across multiple bus ids, regulator/global GPIO power transitions, skew property parsing, DMA error cleanup, and host removal with active slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cavium.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cavium.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/cavium.h

## Purpose
`cavium.h` is the shared private interface and register-definition header for Cavium OCTEON and ThunderX MMC/eMMC drivers. It defines the common host/slot structures, register offset macros, bitfield masks, command/response type helper structs, and exported shared-core prototypes used by both bus-specific front ends.

## Important APIs, Types, and Functions
`struct cvm_mmc_host` describes controller-wide state: device pointer, command and DMA register bases/offsets, cached config, clock frequency, current request, SG iterator, DMA mode flags, feature flags, IRQ lock/serializer, shared power GPIO/accounting, slot arrays, and callback hooks for power, bus locking, interrupt enabling, and DMA erratum handling. `struct cvm_mmc_slot` describes per-slot MMC state: `mmc_host`, parent host, cached clock, cached switch/RCA values, sample-delay counts, and bus id. `struct cvm_mmc_cr_type` and `struct cvm_mmc_cr_mods` support command/response type override calculation.

The header declares `cvm_mmc_interrupt`, `cvm_mmc_of_slot_probe`, `cvm_mmc_of_slot_remove`, and `cvm_mmc_irq_names`.

## Control Flow and State
The header itself has no executable flow, but its macros define how shared code computes addresses for `MIO_EMM_*` command, response, switch, watchdog, sample, buffer, and DMA registers. The `reg_off` and `reg_off_dma` fields allow the same macros to work for OCTEON and ThunderX layouts. Bitfield definitions describe command submission, DMA setup, response status, interrupt bits, switch configuration, FIFO commands, and DMA config.

## State and Persistence Behavior
No persistence is implemented. The structures define all volatile state that survives between callbacks while the driver is loaded: active request state, per-slot cached hardware settings, shared power user count, and feature flags. Callback fields are the abstraction boundary between common code and platform/PCI front ends.

## Dependencies and Integration Points
The header includes Linux bitops, clk, GPIO, IO, MMC host, OF, scatterlist, and semaphore headers. It is included by `cavium.c`, `cavium-octeon.c`, and `cavium-thunderx.c`. Its register macros are tightly coupled to Cavium MIO_EMM hardware documentation and to `FIELD_PREP`/`FIELD_GET` use in the implementation.

## Risks and Test Signals
Risks include mismatched offsets for a front end, incorrect bit masks causing silent hardware programming failures, callback fields left unset, and structure changes that break common/front-end contracts. Test signals are mostly compile- and integration-level: both OCTEON and ThunderX build, register offsets produce expected MMIO access on each platform, all exported prototypes match definitions, max slot count bounds are respected, and interrupt-name indexing matches requested IRQ vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cavium.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cb710-mmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/cb710-mmc.c

## Purpose
`cb710-mmc.c` implements the MMC/SD portion of the ENE CB710 memory card reader driver. It is a PIO-only host driver built on the parent CB710 slot/chip abstraction, with many register behaviors inferred from hardware and the Windows driver. It handles command encoding, response decoding, data PIO, power sequencing, card-change IRQs, and platform-driver registration.

## Important APIs, Types, and Functions
The driver uses `struct cb710_mmc_reader` from `cb710-mmc.h` for active request, IRQ lock, finish work, and last power mode. MMC callbacks are `cb710_mmc_request`, `cb710_mmc_set_ios`, `cb710_mmc_get_ro`, and `cb710_mmc_get_cd`. Important helpers include `cb710_mmc_select_clock_divider`, `cb710_mmc_enable_irq`, `cb710_wait_for_event`, `cb710_wait_while_busy`, `cb710_mmc_set_transfer_size`, `cb710_mmc_fifo_hack`, `cb710_mmc_receive`, `cb710_mmc_send`, `cb710_encode_cmd_flags`, `cb710_receive_response`, `cb710_mmc_command`, `cb710_mmc_powerup`, `cb710_mmc_powerdown`, `cb710_mmc_irq_handler`, and init/exit/PM callbacks.

## Control Flow and State
Probe allocates an MMC host, reads PCI config to derive clock limits, initializes the finish work and IRQ lock, disables MMC IRQ sources, installs a CB710 slot IRQ handler, adds the MMC host, and enables card insertion status IRQs. Requests are synchronous in the request callback: set `reader->mrq`, enable test IRQs, run `cb710_mmc_command` for the main command and optional stop command, then schedule bottom-half work to call `mmc_request_done`.

Command execution waits for busy bits, writes command type and argument registers, resets event status, starts the command through config, waits for command-sent, decodes responses, and performs data transfer if present. Reads and writes use SG mapping iterators and 32-bit data-port helpers; reads apply a FIFO hack that discards two dwords to avoid prepended zeroes. Card-change IRQs acknowledge status and call `mmc_detect_change`.

## State and Persistence Behavior
State is volatile: active `mrq`, last power mode, IRQ enable register state, workqueue completion, and hardware config/status ports. No durable persistence exists. Power-up/down writes a sequence of magic config bits with delays and retries because register behavior is poorly understood. Clock divider state is programmed through PCI config register `0x40` using a source frequency from PCI config `0x48`.

## Dependencies and Integration Points
The driver depends on the CB710 core APIs (`cb710_read_port_*`, `cb710_write_port_*`, `cb710_modify_port_*`, slot/chip conversion, IRQ handler registration, dump helpers, SG data-port iterators), Linux MMC core, PCI config access, workqueues, delays, and platform-driver PM. It advertises 4-bit data, 3.2-3.4 V OCR, and a fixed busy timeout corresponding to its polling loops.

## Risks and Test Signals
Risks include guessed register semantics, fixed polling timeouts, no DMA, special-case transfer-size limits, FIFO workaround fragility, synchronous request work in MMC callback context, and interrupt enable locking that protects only one register. Test signals include probe/init, card insertion/removal IRQs, power-up retry behavior, 1-bit/4-bit mode, command responses including 136-bit shifts and opcode validation, supported/unsupported block sizes, read FIFO alignment cases, write PIO, suspend/resume IRQ disablement, and clean exit with pending finish work canceled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cb710-mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cb710-mmc.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/cb710-mmc.h

## Purpose
`cb710-mmc.h` is the private header for the ENE CB710 MMC/SD subdriver. It defines the per-reader state, slot/MMC conversion helpers, and the inferred CB710 MMC register map used by `cb710-mmc.c`.

## Important APIs, Types, and Functions
`struct cb710_mmc_reader` contains `finish_req_bh_work`, the active `mmc_request`, `irq_lock`, and `last_power_mode`. `cb710_slot_to_mmc` gets the `mmc_host` from a CB710 platform slot, and `cb710_mmc_to_slot` walks from `mmc_host` device to platform device and then to `struct cb710_slot`.

The rest of the header defines port offsets and bit masks for data, config, IRQ enable, status, command type, command argument, transfer size, and response registers. Command definitions include response type, response-present, MMC command type, read-data bit, opcode shift/mask, app-command bit, and busy-response bit.

## Control Flow and State
The header has no active control flow. Its conversion helpers are inline and are used throughout request, IRQ, IOS, and probe paths to bridge Linux MMC core objects and the CB710 core slot abstraction. Register constants guide all hardware access in `cb710-mmc.c`.

## State and Persistence Behavior
No durable persistence is defined. The header defines volatile runtime state and hardware register state only. `last_power_mode` lets the implementation avoid repeating power sequences for unchanged IOS power mode; `irq_lock` serializes IRQ enable updates.

## Dependencies and Integration Points
The header depends on `<linux/cb710.h>` for slot/chip types and on workqueues for the finish work. It is consumed by the platform driver implementation and is coupled to the CB710 core’s platform-device model. The register definitions are marked as potentially inaccurate by comments, reflecting reverse-engineered hardware behavior.

## Risks and Test Signals
Risks include incorrect register definitions, bit masks that overlap unintentionally, helper assumptions about platform driver data, and changing CB710 core types. Test signals include successful compile with CB710 core, correct slot/MMC pointer round-trips, IRQ enable/status bit behavior on card changes, response register decoding, and no regressions in suspend/resume paths that rely on these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/cb710-mmc.h -->
