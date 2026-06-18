# subset-b-005485 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd_intr.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd_intr.c

## Purpose
`hcd_intr.c` implements DWC2 host-mode interrupt handling. It turns core interrupt status bits, port events, FIFO events, and per-host-channel interrupts into URB progress, QTD/QH scheduling changes, channel release, transfer completion, retry, or error completion. It is the interrupt-side partner of the host queueing and transaction programming code.

## Important APIs, Types, And Functions
- Exported entry point: `dwc2_handle_hcd_intr()` is called by the common interrupt handler when host-mode HCD processing is possible.
- Channel dispatch: `dwc2_hc_intr()` reads `HAINT` and services split transactions in `hsotg->split_order` before scanning all channels; `dwc2_hc_n_intr()` reads and clears `HCINT(n)` bits, validates the channel/QTD, and invokes specific handlers.
- Core interrupt handlers: `dwc2_sof_intr()`, `dwc2_rx_fifo_level_intr()`, `dwc2_np_tx_fifo_empty_intr()`, `dwc2_perio_tx_fifo_empty_intr()`, and `dwc2_port_intr()`.
- Transfer state helpers: `dwc2_get_actual_xfer_length()`, `dwc2_update_urb_state()`, `dwc2_update_urb_state_abn()`, `dwc2_update_isoc_urb_state()`, and exported `dwc2_hcd_save_data_toggle()`.
- Channel lifecycle helpers: `dwc2_halt_channel()`, `dwc2_release_channel()`, `dwc2_deactivate_qh()`, `dwc2_complete_non_periodic_xfer()`, and `dwc2_complete_periodic_xfer()`.
- Error/event handlers: `dwc2_hc_xfercomp_intr()`, `dwc2_hc_stall_intr()`, `dwc2_hc_nak_intr()`, `dwc2_hc_ack_intr()`, `dwc2_hc_nyet_intr()`, `dwc2_hc_babble_intr()`, `dwc2_hc_ahberr_intr()`, `dwc2_hc_xacterr_intr()`, `dwc2_hc_frmovrun_intr()`, `dwc2_hc_datatglerr_intr()`, and `dwc2_hc_chhltd_intr_dma()`.

## Control Flow
`dwc2_handle_hcd_intr()` first checks controller liveness, then takes `hsotg->lock` and confirms host mode. It reads masked core interrupts with `dwc2_read_core_intr()` and handles SOF, Rx FIFO, non-periodic FIFO empty, port, host-channel, and periodic FIFO empty interrupts in a fixed order. SOF updates `hsotg->frame_number`, tracks missed SOFs, moves ready periodic QHs from inactive to ready, selects transactions, and queues work.

Host-channel interrupts are two-level. `dwc2_hc_intr()` reads `HAINT`, handles channels in split-completion order first to preserve USB 2.0 TT ordering, then handles remaining channels by index. `dwc2_hc_n_intr()` reads raw and masked channel interrupt bits, writes the masked bits back to clear them, validates `chan`, `chan->qh`, and the active QTD, and then processes bits by priority. It rechecks whether the original QTD is still at the QH head after handlers that may complete and free/unlink it.

Transfer-complete handling is endpoint-specific. Control transfers advance setup, data, and status phases; bulk and interrupt transfers update `urb->actual_length` and data toggle; isochronous transfers update per-frame status and length. Non-periodic completions normally release or halt and release the channel so the scheduler can assign it again. Periodic completions either release immediately or halt first if outstanding IN packets remain.

## State And Persistence Behavior
The file mutates transient in-memory HCD state: URB status and `actual_length`, QTD fields such as `control_phase`, `complete_split`, `isoc_frame_index`, `error_count`, `num_naks`, and `want_wait`, QH fields such as `data_toggle`, `ping_state`, `tt_buffer_dirty`, and channel fields such as `halt_status`, `xfer_count`, `xfer_buf`, and `hcint`. It updates host controller counters and lists through `dwc2_release_channel()` and `dwc2_hcd_qh_deactivate()`, including free-channel lists, non-periodic/periodic schedule lists, `available_host_channels`, and non-periodic channel counters. Hardware state is persisted only in controller registers such as `GINTSTS`, `GINTMSK`, `HPRT0`, `HCFG`, `HFIR`, `HAINTMSK`, `HCINT`, and `HCTSIZ`.

## Dependencies And Integration Points
This code depends on DWC2 register definitions from `hw.h`, host data structures and helpers from `core.h` and `hcd.h`, USB core URB and TT APIs, Linux spinlocks, DMA mapping, and workqueue/timer interactions created elsewhere. It calls scheduler functions from host queue code (`dwc2_hcd_select_transactions()`, `dwc2_hcd_queue_transactions()`, `dwc2_hcd_qh_deactivate()`), transfer completion helpers (`dwc2_host_complete()`), DDMA helpers (`dwc2_hcd_complete_xfer_ddma()`), and core helpers for mode, frame number, FIFO, TT clear, and channel halt/cleanup.

## Risks
- QTD/QH lifetime is fragile in interrupt context. The explicit `dwc2_check_qtd_still_ok()` calls show that handlers may complete and free the active QTD; any new handler ordering must preserve this validation.
- Split transaction handling is latency-sensitive and order-sensitive. Changing `split_order` handling or NYET/NAK retry logic risks TT protocol regressions.
- DMA and slave mode paths differ substantially. A fix for one path can break the other if channel halt/release semantics are assumed to be identical.
- Actual-length calculation depends on correct interpretation of `HCTSIZ` fields after halt; using AHB byte count for abnormal halts would corrupt URB progress.
- Port enable handling can reset the port when FS/LS low-power clock settings change. Bad sequencing here can cause reconnect loops or descriptor DMA mode toggling problems.
- Error retry policy uses a three-strikes `qtd->error_count` rule and NAK delay threshold; changing it can cause interrupt storms or premature URB failure.

## Test Signals
- Exercise control, bulk, interrupt, and isochronous transfers in host mode, both DMA and non-DMA if platform supports them.
- Test high-speed hub with full-/low-speed devices to cover split ordering, TT clear, NAK/NYET, and isochronous split paths.
- Validate port connect, enable change, overcurrent change, reset, and FS/LS low-power clock paths with real devices.
- Stress with devices that NAK repeatedly and confirm retry delay prevents interrupt storms without control-IN stalls.
- Enable debug or tracing around HC interrupts to verify no "Interrupt on disabled channel", "no QTD queued", or unknown halt reason messages appear under normal load.
- Use error injection or flaky devices to cover STALL, babble, AHB error, transaction error, frame overrun, and data toggle error completion status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd_intr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd_queue.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd_queue.c

## Purpose
`hcd_queue.c` owns host-side Queue Head and Queue Transfer Descriptor management for DWC2. It builds QHs from URB endpoint metadata, adds/removes QTDs, reserves and releases periodic bandwidth, computes microframe schedules for high-speed and split transactions, and moves QHs among inactive, ready, assigned, queued, waiting, and unreserved states.

## Important APIs, Types, And Functions
- Public QH/QTD APIs: `dwc2_hcd_qh_create()`, `dwc2_hcd_qh_free()`, `dwc2_hcd_qh_add()`, `dwc2_hcd_qh_unlink()`, `dwc2_hcd_qh_deactivate()`, `dwc2_hcd_qtd_init()`, and `dwc2_hcd_qtd_add()`.
- Periodic reservation: `dwc2_schedule_periodic()`, `dwc2_deschedule_periodic()`, `dwc2_do_reserve()`, `dwc2_do_unreserve()`, and `dwc2_unreserve_timer_fn()`.
- Bitmap scheduler: `pmap_schedule()` and `pmap_unschedule()` reserve repeating time slices in high-speed or low/full-speed maps using `gcd(interval, periods_in_map)`.
- Split scheduling: `dwc2_uframe_schedule_split()` coordinates TT-side low/full-speed time and high-speed start/complete split slots.
- High-speed and low-speed wrappers: `dwc2_uframe_schedule_hs()`, `dwc2_uframe_schedule_ls()`, `dwc2_uframe_schedule()`, and `dwc2_uframe_unschedule()`.
- Frame progression: `dwc2_pick_first_frame()`, `dwc2_next_for_periodic_split()`, and `dwc2_next_periodic_start()`.
- Retry timer: `dwc2_wait_timer_fn()` moves NAK-delayed non-periodic QHs back to the inactive schedule.

## Control Flow
URB submission creates or reuses a QH, initializes endpoint attributes in `dwc2_qh_init()`, initializes a QTD with `dwc2_hcd_qtd_init()`, then attaches it with `dwc2_hcd_qtd_add()`. Adding a QTD first ensures the QH is scheduled via `dwc2_hcd_qh_add()`. Non-periodic QHs enter the inactive list immediately unless `want_wait` is set, in which case they enter the waiting list and an hrtimer later requeues them. Periodic QHs call `dwc2_schedule_periodic()`.

Periodic scheduling first validates maximum transfer size, cancels pending delayed unreserve if present, and reserves bandwidth if needed. With `uframe_sched` enabled, `dwc2_uframe_schedule()` chooses high-speed, low/full-speed, or split scheduling. Without it, reservation is a simpler channel-count plus aggregate-usec check. Once reserved, `dwc2_pick_first_frame()` chooses `next_active_frame`, then the QH is linked into ready or inactive periodic lists depending on descriptor DMA and frame timing.

Split scheduling is the most complex path. It schedules the low-speed TT map first, rejects illegal or unsupported placements, derives high-speed start split and complete split microframes, estimates per-microframe durations, then reserves matching high-speed slots. If high-speed placement fails, it rolls back all partial reservations, unschedules the low-speed slot, advances the low-speed search position, and retries.

Deactivation is called from interrupt-side completion. Non-periodic QHs are unlinked and re-added if QTDs remain. Periodic QHs compute the next frame, account for missed frames, and either unlink if empty or move to ready/inactive based on `next_active_frame`.

## State And Persistence Behavior
All state is in memory and protected by `hsotg->lock` where required. The file mutates QH fields including endpoint type/direction, speed, max packet values, split/TT metadata, `host_us`, `device_us`, intervals, schedule map positions, `hs_transfers[]`, active frame numbers, `want_wait`, and `unreserve_pending`. It mutates HCD counters and bitmaps such as `periodic_channels`, `non_periodic_channels`, `periodic_usecs`, `periodic_qh_count`, `hs_periodic_bitmap`, and TT `periodic_bitmaps`. It also starts/cancels kernel timers for delayed unreserve and NAK retry. There is no disk persistence.

## Dependencies And Integration Points
The code integrates with `hcd_intr.c`, which calls `dwc2_hcd_qh_deactivate()` after transfer interrupts, and with transaction-selection code that consumes the schedule lists. It uses USB core helpers such as `usb_calc_bus_time()`, TT metadata from `dwc2_host_get_tt_info()` and `dwc2_host_put_tt_info()`, Linux bitmap APIs, timers/hrtimers, DMA descriptor initialization/free helpers, DWC2 frame-number helpers, and register access for `HPRT0` and `GINTMSK`.

## Risks
- `pmap_schedule()` relies on `gcd()` adjustment to handle intervals not aligned to map size. Bugs here can overcommit periodic bandwidth or reject valid schedules.
- Split scheduling assumptions explicitly skip some partial OUT cases because other DWC2 code cannot handle them. Removing those guards without fixing transfer code can break interrupt and isochronous devices behind hubs.
- Delayed unreserve uses timer and lock races intentionally. Incorrect cancellation or freeing order can lead to use-after-free or leaked bandwidth reservations.
- `dwc2_next_periodic_start()` handles missed frames under tight interrupt-latency assumptions; changes can duplicate periodic transfers in the same frame or starve endpoints.
- `dwc2_hcd_qh_free()` must not be called with the spinlock held because it waits for timers; violating that contract can deadlock.
- Schedule list membership is encoded by `qh_list_entry` emptiness and list position. Incorrect list movement can make transactions disappear or double schedule.

## Test Signals
- Run USB host tests with interrupt and isochronous devices at high, full, and low speed, including devices behind single-TT and multi-TT hubs.
- Stress URB submit/complete loops to verify delayed unreserve preserves bandwidth for quick resubmission and releases it after idle.
- Trigger repeated NAKs and confirm `want_wait` hrtimer requeues QHs without CPU interrupt storms.
- Enable `DWC2_PRINT_SCHEDULE` or schedule debug output to inspect high-speed and low-speed bitmaps after scheduling and unscheduling.
- Test large periodic endpoints near `max_transfer_size` and bus-time limits to confirm `-ENOSPC` behavior is deterministic.
- Exercise endpoint disable/dequeue while timers are pending to catch list and timer lifetime regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/hw.h -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/hw.h

## Purpose
`hw.h` is the DWC2 hardware register and bitfield definition header. It defines global, device-mode, host-mode, power-management, FIFO, endpoint/channel, transfer-size, and DMA descriptor constants used throughout the DWC2 core, host, gadget, platform, and parameter code.

## Important APIs, Types, And Functions
- Register address macro: `HSOTG_REG(x)` and register offsets such as `GOTGCTL`, `GAHBCFG`, `GUSBCFG`, `GRSTCTL`, `GINTSTS`, `GINTMSK`, `GHWCFG1-4`, `GLPMCFG`, `GPWRDN`, `HCFG`, `HFIR`, `HFNUM`, `HPRT0`, `HCCHAR(ch)`, `HCSPLT(ch)`, `HCINT(ch)`, `HCINTMSK(ch)`, `HCTSIZ(ch)`, and endpoint register macros.
- Bit masks and shifts for global interrupts, OTG state, reset, FIFO sizing, hardware configuration discovery, LPM, power-down, device endpoint control, host port control, host channel control, split transactions, and transfer sizes.
- Helper getter macros such as `FIFOSIZE_DEPTH_GET()`, `GNPTXSTS_NP_TXQ_SPC_AVAIL_GET()`, `DXEPTSIZ_PKTCNT_GET()`, and `DXEPTSIZ_XFERSIZE_GET()`.
- DMA type: `struct dwc2_dma_desc { u32 status; u32 buf; } __packed`.
- Host and device DMA descriptor status masks such as `HOST_DMA_A`, `HOST_DMA_IOC`, `HOST_DMA_NBYTES_MASK`, `DEV_DMA_BUFF_STS_MASK`, `DEV_DMA_STS_MASK`, and isochronous byte/count fields.

## Control Flow
This header has no executable control flow. It provides the symbolic interface used by C files that read, write, mask, shift, and compose DWC2 memory-mapped registers. Runtime flow emerges in callers: platform code validates `GSNPSID`, params code decodes `GHWCFG*`, host interrupt code decodes `GINTSTS`, `HPRT0`, `HCINT`, and `HCTSIZ`, queue code reads `HPRT0`, and gadget code uses endpoint definitions.

## State And Persistence Behavior
The header itself stores no state. The constants describe persistent hardware state in memory-mapped registers and DMA descriptors owned by the controller and driver. Correctness depends on masks and shifts matching the IP revision. The packed DMA descriptor layout is an ABI between CPU memory and DWC2 DMA engines.

## Dependencies And Integration Points
`hw.h` expects kernel bit macros such as `BIT()` and `GENMASK()` to be available through including headers. It is included indirectly through DWC2 core headers by most driver components. `params.c` depends on `GHWCFG*`, `FIFOSIZE_*`, and core revision masks to derive capabilities. `hcd_intr.c` and host code rely on host-channel and interrupt constants. Platform suspend/resume and power code use `GOTGCTL`, `GUSBCFG`, `GGPIO`, `PCGCTL`, and power-down bits.

## Risks
- Register aliases and overlapping bit definitions are intentional in several places, such as packet status values and endpoint interrupt bits. Callers must use the right symbolic name for host vs device context.
- Incorrect masks or shifts corrupt hardware programming globally; this header has high blast radius.
- Some constants encode hardware quirks or misspellings from register names, so cleanup can break code that mirrors documentation naming.
- DMA descriptor fields have different meanings for host/gadget and generic/isoc transfers. Reusing the wrong mask can produce data corruption.
- Channel and endpoint register macros assume a fixed stride; any IP variant with different layout would need separate handling.

## Test Signals
- Compile coverage is a primary signal: all DWC2 host/gadget/platform objects should build with no undefined or type issues.
- Runtime validation comes from successful core version and hardware parameter detection in probe.
- Host and gadget transfer tests validate the HC/EP masks and transfer-size fields indirectly.
- DMA and descriptor-DMA transfer tests validate descriptor layout and host/device DMA status constants.
- Suspend/resume and low-power tests exercise `GLPMCFG`, `GPWRDN`, `PCGCTL`, and restore-related bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/params.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/params.c

## Purpose
`params.c` detects DWC2 hardware capabilities, derives default core parameters, applies platform-specific overrides from OF/ACPI/PCI match data, reads firmware properties, validates parameters against hardware limits, and exports match tables used by platform and PCI glue.

## Important APIs, Types, And Functions
- Match tables: `dwc2_of_match_table`, `dwc2_acpi_match`, and exported `dwc2_pci_ids`.
- Platform override callbacks: `dwc2_set_bcm_params()`, `dwc2_set_his_params()`, Ingenic, Loongson, Samsung, Intel SoCFPGA, Rockchip, Lantiq, Amlogic, AMCC/APM, Sophgo, and STM32 parameter setters.
- Default derivation: `dwc2_set_default_params()` calls helpers for OTG caps, PHY type, speed, UTMI width, power-down, LPM, FIFO defaults, DMA capability, and host/gadget defaults.
- Firmware properties: `dwc2_get_device_properties()` reads gadget FIFO sizes, OTG capabilities, and overcurrent disable.
- Validation: `dwc2_check_params()` plus helpers such as `dwc2_check_param_otg_cap()`, `dwc2_check_param_phy_type()`, `dwc2_check_param_speed()`, `dwc2_check_param_power_down()`, `dwc2_check_param_tx_fifo_sizes()`, and `dwc2_check_param_eusb2_disc()`.
- Hardware discovery: public `dwc2_get_hwparams()` and private `dwc2_get_host_hwparams()` / `dwc2_get_dev_hwparams()`.
- Public initialization: `dwc2_init_params()`.

## Control Flow
Probe calls `dwc2_get_hwparams()` after core reset. That function reads `GHWCFG1-4` and `GRXFSIZ`, decodes op mode, architecture, FIFO depth, host channel count, PHY support, DMA descriptor support, power/LPM capabilities, and maximum transfer/packet counts. It temporarily forces host or device mode where needed to read mode-specific reset FIFO values.

Later `dwc2_init_params()` sets hardware-derived defaults, reads firmware properties, applies an OF/ACPI match callback when present, or PCI driver data when applicable. It then applies maximum-speed policy from `usb_get_maximum_speed()` and calls `dwc2_check_params()` to clamp invalid values back to supported defaults or disable unsupported booleans.

The platform setter callbacks are narrow tables of SoC-specific corrections. They tune FIFO sizes, DMA enablement, PHY type and width, power-down mode, burst length, LPM features, overcurrent/ID/VBUS detection quirks, and low-power FS/LS host behavior.

## State And Persistence Behavior
The file populates `hsotg->hw_params` and `hsotg->params`, both runtime in-memory structures used by the rest of the driver. `hw_params` is derived from controller registers; `params` is derived from hardware, firmware, and match data. There is no disk persistence. Some fields become long-lived policy for the controller lifetime, such as DMA mode, FIFO sizes, host channel count, PHY choice, LPM, power-down strategy, and platform quirks.

## Dependencies And Integration Points
`platform.c` uses the OF and ACPI match tables and calls `dwc2_get_hwparams()` and `dwc2_init_params()` during probe. `pci.c` uses `dwc2_pci_ids`. Host interrupt and queue code depend on `params.host_dma`, `params.dma_desc_enable`, `params.uframe_sched`, FIFO sizes, max transfer sizes, and FS/LS low-power settings. Gadget code depends on gadget FIFO and DMA params. The code uses firmware property APIs, USB OF helpers, generic PHY bus-width query, PCI ID matching, and DWC2 register definitions from `hw.h`.

## Risks
- `dwc2_set_param_phy_type()` assigns FS for FS-only cases but then unconditionally assigns `val`; this pattern depends on `val` already representing the intended fallback.
- Hardware mode forcing during parameter reads must happen immediately after reset; calling it later could disturb active operation.
- Platform overrides can disable DMA/LPM/power features for correctness. Removing or generalizing them risks regressions on specific SoCs.
- Validation macros silently replace invalid values with defaults after warnings. Bad defaults can hide firmware errors until runtime.
- FIFO size validation must respect total depth and per-FIFO hardware sizes; mistakes can cause endpoint allocation or transfer failures.
- PCI fallback assumes parent device is a PCI device when no match data exists.

## Test Signals
- Probe logs should show valid core release and no invalid-parameter warnings for known-good device trees.
- Boot host, gadget, and dual-role configurations across representative SoCs or emulated configs.
- Validate FIFO sizing by running gadget endpoints with multiple TX FIFOs and host transfers using periodic/non-periodic FIFOs.
- Test maximum-speed firmware limits, especially full-speed forcing and invalid low-speed forcing.
- Confirm platform-specific quirks: STM32 ID/VBUS detection, Ingenic overcurrent property, Loongson partial power-down, CV1800 non-DMA mode, and Rockchip LPM disable.
- Build with OF, ACPI, and PCI combinations to verify exported match tables and fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/pci.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/pci.c

## Purpose
`pci.c` is a PCI glue driver for DWC2. It binds supported PCI IDs, enables the PCI device, registers a generic USB PHY, creates a child platform device named `dwc2` with MMIO and IRQ resources, and lets the main DWC2 platform driver handle the actual controller.

## Important APIs, Types, And Functions
- Driver name: `dwc2-pci`.
- Glue state: `struct dwc2_pci_glue` stores the child DWC2 platform device and generic PHY platform device.
- Probe: `dwc2_pci_probe()` enables PCI, sets bus mastering, registers generic PHY, allocates and populates the `dwc2` platform device, attaches BAR0 and IRQ resources, and stores glue state with `pci_set_drvdata()`.
- Remove: `dwc2_pci_remove()` unregisters the child platform device and generic PHY.
- Module registration: `module_pci_driver(dwc2_pci_driver)` uses `dwc2_pci_ids` from `params.c`.

## Control Flow
When a supported PCI device appears, `pcim_enable_device()` enables it and managed PCI cleanup is established. The driver marks the device bus-master capable, registers a generic USB PHY, allocates a platform device, creates two resources from BAR0 and `pci->irq`, assigns the PCI device as parent, adds resources, adds the platform device, then stores the glue. On any failure after PHY registration, it unregisters the PHY and drops the platform device reference. Removal reverses successful probe by unregistering the platform child and PHY.

## State And Persistence Behavior
The only persistent runtime state is `struct dwc2_pci_glue` allocated with devm memory and referenced as PCI driver data. Hardware resource state is managed by PCI core, the generic PHY registration, and the child platform device. There is no file persistence.

## Dependencies And Integration Points
This file depends on `dwc2_pci_ids` exported by `params.c`, Linux PCI APIs, platform device APIs, and `usb_phy_generic_register()`. Its main integration point is `platform.c`: the child device name `dwc2` must match the platform driver, and its parent remains the PCI device so `dwc2_init_params()` can find PCI match data through `to_pci_dev(hsotg->dev->parent)`.

## Risks
- Error unwinding must avoid unregistering or putting invalid platform device pointers. The current `err` path handles both after allocation attempts, but future edits must keep order precise.
- The child platform device receives only BAR0 and one IRQ. Multi-resource variants would need explicit support.
- The code registers a generic PHY unconditionally for PCI devices. Platforms needing a more specific PHY model may require different glue.
- Parent-child relationship is semantically important for parameter matching and DMA/resource behavior.

## Test Signals
- Build with `CONFIG_USB_DWC2_PCI` and supported PCI IDs.
- Probe on Synopsys HAPS, STMicro, or Loongson DWC2 PCI devices and verify the child `dwc2` platform driver binds.
- Remove/unbind the PCI driver and check that the child platform device and generic PHY unregister cleanly.
- Validate BAR0 MMIO mapping and IRQ delivery through successful platform probe and host/gadget operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/platform.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/platform.c

## Purpose
`platform.c` is the main platform driver for DWC2. It owns resource acquisition, low-level hardware enable/disable, core validation, hardware parameter discovery, IRQ registration, role-mode selection, HCD/gadget/dual-role initialization, debugfs setup, removal/shutdown, and system suspend/resume.

## Important APIs, Types, And Functions
- Driver name and registration: `dwc2_platform_driver` and `module_platform_driver()`.
- Mode selection: `dwc2_get_dr_mode()` reconciles firmware `dr_mode`, hardware capability, and Kconfig host/peripheral support.
- Resource control: `dwc2_lowlevel_hw_init()`, `dwc2_lowlevel_hw_enable()`, `dwc2_lowlevel_hw_disable()`, and internal `__dwc2_lowlevel_hw_enable()` / `__dwc2_lowlevel_hw_disable()`.
- Lifecycle: `dwc2_driver_probe()`, `dwc2_driver_remove()`, and `dwc2_driver_shutdown()`.
- Core validation: `dwc2_check_core_endianness()` and public `dwc2_check_core_version()`.
- Power management: `dwc2_suspend()`, `dwc2_resume()`, and `dwc2_restore_critical_registers()`.

## Control Flow
Probe allocates `struct dwc2_hsotg`, sets a 32-bit coherent DMA mask, maps the first platform resource, initializes resets/PHYs/clocks/regulators, initializes the spinlock, optionally gets VBUS, and enables low-level hardware. It detects byte swapping, resolves `dr_mode`, reads wake quirks, validates `GSNPSID`, resets the core, reads hardware parameters, requests a shared IRQ for `dwc2_handle_common_intr`, forces the configured DRD mode, initializes params, applies STM32 ID/VBUS detection setup if enabled, initializes dual-role support, then initializes gadget and/or HCD depending on mode. Debugfs is created after core components are up, peripheral-only mode releases low-level hardware to gadget management, and gadget registration is finally exposed to UDC.

Remove exits hibernation, partial power-down, or clock gating as needed before tearing down debugfs, HCD, gadget, dual-role, STM32 regulators, and low-level hardware. Shutdown disables global interrupts, synchronizes the IRQ, and powers down resources to avoid interrupt storms during reboot/poweroff.

Suspend first exits active gadget state and DRD, handles STM32 ID/VBUS detection overrides, backs up critical host or gadget registers, and may power off PHY/resources if safe. Resume re-enables resources when powered off, restores critical registers if power-domain loss is detected through `GUSBCFG`, restores STM32 detection, reasserts force mode or resumes role-switch state, and resumes gadget mode if active.

## State And Persistence Behavior
The driver stores runtime state in `struct dwc2_hsotg`, including mapped registers, IRQ, clocks, PHY handles, regulators, reset controls, `ll_hw_enabled`, role flags, wake quirks, byte-swap flag, HCD/gadget enabled flags, hibernation/partial-power-down state, register backups, and suspend flags such as `phy_off_for_suspend`. Register backups are volatile memory used across system sleep; there is no disk persistence.

## Dependencies And Integration Points
This file integrates with Linux platform, device property, clock, reset, regulator, generic PHY, old USB PHY, DMA, IRQ, PM, and OF/ACPI subsystems. It calls core DWC2 functions for reset, interrupts, mode forcing, DRD, HCD, gadget, debugfs, hibernation, partial power-down, clock gating, and register backup/restore. It consumes match tables from `params.c` and register definitions from `hw.h`.

## Risks
- Probe ordering is strict. `dwc2_get_hwparams()` must follow core reset; IRQ registration must happen after core validation but before active controller components.
- `ll_hw_enabled` is used to gate removal, shutdown, suspend, and resume behavior. Incorrect updates can double-disable resources or leave hardware powered unexpectedly.
- Mode reconciliation combines hardware, Kconfig, and firmware. Wrong assumptions can register unsupported host/gadget roles.
- Suspend/resume handles several power states and platform quirks. Missing register restore after power-domain loss can leave the controller half-configured.
- STM32 ID/VBUS detection toggles regulators and `GGPIO`/`GOTGCTL` bits; bad sequencing can create mode mismatch interrupts or lost wake/session state.
- PCI-created platform devices rely on this driver accepting resources and parent relationships that did not originate from OF.

## Test Signals
- Boot/probe in host-only, gadget-only, and dual-role builds with matching and mismatching `dr_mode`.
- Validate probe failure paths with missing clocks, PHY defer, regulator failure, bad `GSNPSID`, and IRQ failure.
- Runtime test host and gadget enumeration, debugfs creation/removal, and dual-role role switching.
- Suspend/resume with and without PHY poweroff, wake-enabled devices, power-domain register loss, and STM32 ID/VBUS detection.
- Shutdown/reboot with attached hubs or interrupt-heavy devices to confirm global interrupts are disabled.
- Unbind/remove while hibernated, in partial power-down, or bus-suspended to verify cleanup exits low-power states first.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/Kconfig

## Purpose
`drivers/usb/dwc3/Kconfig` defines the build-time configuration menu for the DesignWare USB3 DRD core and its platform glue drivers. It controls whether the DWC3 core is built, whether host/gadget/dual-role support is compiled, whether ULPI support is enabled, and which SoC or bus glue modules participate in the build.

## Important Symbols
- `USB_DWC3`: top-level tristate for the DWC3 core, depending on USB or USB_GADGET plus DMA support and compatible EXTCON state. It selects xHCI platform support when host xHCI is enabled and role-switch support for dual-role mode.
- `USB_DWC3_ULPI`: optional ULPI PHY interface registration when the ULPI bus is available.
- Mode choice: `USB_DWC3_HOST`, `USB_DWC3_GADGET`, and `USB_DWC3_DUAL_ROLE`, with defaults based on available USB host/gadget subsystems.
- Glue symbols: OMAP, Exynos, PCI, HAPS, Keystone, Meson G12A, OF Simple, ST, Qualcomm, i.MX8MP, i.MX, Xilinx, AM62, Octeon, Realtek, generic platform, Apple, and Google platform support.

## Control Flow
Kconfig has declarative control flow. Enabling `USB_DWC3` opens the mode choice and platform glue menu. The mode choice determines which core source files the Makefile includes. Glue options default to `USB_DWC3` where appropriate but are constrained by architecture, OF, ACPI, PCI, COMMON_CLK, EXTCON, and COMPILE_TEST availability.

## State And Persistence Behavior
Selected symbols are persisted in the kernel `.config`, not in runtime driver state. Those symbols control which objects compile into the kernel or modules and which runtime capabilities exist. For example, selecting host-only removes gadget objects from the DWC3 core build, while dual-role selects role-switch support.

## Dependencies And Integration Points
This file directly integrates with `drivers/usb/dwc3/Makefile`, which maps the symbols to objects. It also integrates with USB core, USB gadget, xHCI platform, role-switch, EXTCON, ULPI bus, OF, ACPI, architecture symbols, common clock, and regmap dependencies. The glue symbols correspond to source files such as `dwc3-pci.o`, `dwc3-qcom.o`, `dwc3-of-simple.o`, and related platform objects.

## Risks
- Incorrect dependencies can expose glue drivers on unsupported build combinations or hide them from valid COMPILE_TEST coverage.
- Mode choice dependencies must match Makefile conditions; otherwise a selected mode might omit required objects or include impossible code.
- Defaulting many glue drivers to `USB_DWC3` is convenient but can increase build coverage and module surface; dependency mistakes become broad.
- Role-switch selection is required for dual-role and some platform glues. Missing selects can cause link or runtime role-management failures.

## Test Signals
- Run `allmodconfig`, `allyesconfig`, and targeted host/gadget/dual-role configs to verify symbol dependency consistency.
- Confirm `USB_DWC3=m` builds `dwc3.ko` and selected glue modules as modules.
- Validate host-only excludes gadget/DRD objects, gadget-only excludes host/DRD objects, and dual-role includes host, gadget, and DRD.
- Build platform glue options under COMPILE_TEST where allowed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/Makefile

## Purpose
`drivers/usb/dwc3/Makefile` maps DWC3 Kconfig symbols to object files. It builds the core `dwc3.o` composite object from common, optional tracing, host, gadget, DRD, ULPI, and debugfs pieces, then builds platform-specific glue objects based on their individual symbols.

## Important Build Rules
- `CFLAGS_trace.o := -I$(src)` ensures generated trace definitions can find the local trace header.
- `obj-$(CONFIG_USB_DWC3) += dwc3.o` creates the main composite driver object.
- `dwc3-y := core.o` is always included when DWC3 is enabled.
- Conditional core pieces: `trace.o` for tracing, `host.o` for host or dual-role, `gadget.o ep0.o` for gadget or dual-role, `drd.o` for dual-role, `ulpi.o` for ULPI, and `debugfs.o` for debugfs.
- Glue rules map platform symbols to objects such as `dwc3-am62.o`, `dwc3-apple.o`, `dwc3-pci.o`, `dwc3-qcom.o`, `dwc3-of-simple.o`, `dwc3-generic-plat.o`, and `dwc3-google.o`.

## Control Flow
The Makefile uses kbuild conditional expansion. `obj-*` determines which standalone or composite objects are built. `dwc3-y` appends objects into the composite based on enabled symbols. The `ifneq ($(filter y,...),)` conditions intentionally include host/gadget objects only for built-in `y` mode selections, matching the Kconfig choice semantics inside an enabled DWC3 build.

## State And Persistence Behavior
There is no runtime state. Build state is derived from `.config` and kbuild variables. The output is object files and modules generated by the kernel build system.

## Dependencies And Integration Points
This file depends on the symbols declared in `Kconfig`. It integrates with kbuild composite object conventions and with source files in the same directory. The comment for glue layers documents an integration policy: glue should avoid arch-specific compile dependencies so broad configs continue to build.

## Risks
- Kconfig and Makefile symbols must stay synchronized; adding a symbol without an object rule, or an object rule without a symbol, breaks expected builds.
- Core object inclusion must match mode semantics. Including gadget or host pieces under the wrong condition can cause link failures or unintended functionality.
- `dwc3-qcom` and `dwc3-qcom-legacy` both build under `CONFIG_USB_DWC3_QCOM`; changes to either dependency affect the same symbol.
- Trace include flags are local to `trace.o`; moving trace headers or generated trace definitions requires revisiting `CFLAGS_trace.o`.

## Test Signals
- Build `CONFIG_USB_DWC3=y` and `m` with host-only, gadget-only, and dual-role choices.
- Build with `CONFIG_TRACING`, `CONFIG_DEBUG_FS`, and `CONFIG_USB_DWC3_ULPI` toggled to verify conditional object inclusion.
- Build each glue symbol as built-in and module where possible.
- Run broad kbuild configs to enforce the Makefile comment that glue layers compile across architectures when dependencies allow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/Makefile -->
