# subset-b-005510 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/octeon-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/octeon-hcd.c

## Purpose
`octeon-hcd.c` is a complete Linux USB host-controller driver for Cavium/Marvell OCTEON USB2 hardware. Unlike the OHCI glue files nearby, it does not layer on a generic OHCI core; it implements its own `struct hc_driver` operations, private pipe/transaction scheduler, root-hub emulation, DMA/non-DMA data movement, and OCTEON register bring-up using the register definitions in `octeon-hcd.h`.

## Important APIs, types, and functions
Core private types are defined in this C file: `struct octeon_hcd` is the controller state stored in `usb_hcd.hcd_priv`; `struct cvmx_usb_pipe` models an endpoint pipe and its pending transaction list; `struct cvmx_usb_transaction` tracks a URB-backed transfer, current stage, retry count, byte counts, and ISO packet metadata. Supporting enums model USB speed, transfer type, direction, completion status, initialization flags, pipe flags, and split/control stages.

The Linux HCD interface is exported through `octeon_hc_driver`: `.irq = octeon_usb_irq`, `.start`, `.stop`, `.urb_enqueue`, `.urb_dequeue`, `.endpoint_disable`, `.get_frame_number`, `.hub_status_data`, `.hub_control`, and Octeon-specific DMA map/unmap hooks. Platform integration is through `octeon_usb_probe()`, `octeon_usb_remove()`, the `cavium,octeon-5750-usbc` OF match table, and module init/exit registration.

Hardware setup is concentrated in `cvmx_usb_initialize()`, `cvmx_fifo_setup()`, `cvmx_wait_tx_rx()`, `cvmx_usb_shutdown()`, `cvmx_usb_reset_port()`, `cvmx_usb_disable()`, and `cvmx_usb_get_status()`. Register access goes through `cvmx_usb_read_csr32()`, `cvmx_usb_write_csr32()`, and `USB_SET_FIELD32()`, which hide the OCTEON 32-bit CSR address swizzle.

The scheduling and transfer engine is split across `cvmx_usb_open_pipe()`, `cvmx_usb_submit_transaction()` and its typed wrappers, `cvmx_usb_schedule()`, `cvmx_usb_next_pipe()`, `cvmx_usb_find_ready_pipe()`, `cvmx_usb_start_channel()`, `cvmx_usb_start_channel_control()`, `cvmx_usb_poll()`, `cvmx_usb_poll_channel()`, `cvmx_usb_transfer_control()`, `cvmx_usb_transfer_bulk()`, `cvmx_usb_transfer_intr()`, `cvmx_usb_transfer_isoc()`, `cvmx_usb_complete()`, and `octeon_usb_urb_complete_callback()`. Non-DMA FIFO mode is handled by `cvmx_usb_poll_rx_fifo()`, `cvmx_usb_fill_tx_fifo()`, `cvmx_usb_fill_tx_hw()`, and `cvmx_usb_poll_tx_fifo()`.

## Control flow
Probe validates the device tree, reads the parent USBN clock frequency and reference-clock type, derives `CVMX_USB_INITIALIZE_FLAGS_*`, finds the USB block index from the MMIO resource, recovers an IRQ mapping for known broken DTs if necessary, coerces a 64-bit DMA mask, applies model-specific IOB priority tuning, allocates a `usb_hcd`, initializes `struct octeon_hcd`, selects usable hardware channels based on chip errata, calls `cvmx_usb_initialize()`, and registers the HCD with `usb_add_hcd()`.

URB enqueue links the URB to the endpoint, lazily opens a `cvmx_usb_pipe` in `ep->hcpriv`, computes endpoint type, speed, max packet, interval, high-speed split hub/port information, and then creates a transaction for bulk, interrupt, control, or isochronous URBs. ISO URBs get a private `cvmx_usb_iso_packet` array stored temporarily in `urb->setup_packet`. When a pipe receives its first transaction, it moves from `idle_pipes` to the appropriate `active_pipes[type]` list and scheduling is attempted.

Scheduling chooses ready pipes by priority: on SOF, isochronous then interrupt; always control then bulk. It assigns idle hardware channels, programs channel interrupt masks, DMA pointer registers, split registers, transfer-size registers, host-channel characteristics, and type-specific PID/control-stage details before enabling the channel. SOF interrupts are enabled only when future frame-gated work exists.

Interrupt handling enters `octeon_usb_irq()`, locks `usb->lock`, and calls `cvmx_usb_poll()`. Polling updates the extended frame counter, reads and clears `GINTSTS`, drains/fills FIFOs in non-DMA mode, reports root-hub changes on port/disconnect interrupts, scans `HAINT` for channel interrupts, calls `cvmx_usb_poll_channel()` for each active channel, and schedules more work. Channel polling computes bytes transferred from `HCTSIZ` and `HCCHAR`, updates PID toggles and retry state, classifies STALL/XACTERR/BABBLE/DATATGL/NYET/ACK/NAK/no-status cases, advances control/split stages, and eventually completes or retries the transaction.

Root hub operations are locally emulated for the single OCTEON port. `octeon_usb_hub_control()` answers hub descriptor/status requests, maps port status to Linux `USB_PORT_FEAT_*` and `USB_PORT_STAT_*` bits, drives port power through `HPRT.prtpwr`, resets the port through `cvmx_usb_reset_port()`, disables the port through `cvmx_usb_disable()`, and clears internal change state by refreshing `usb->port_status`.

## State and persistence behavior
All runtime state is volatile kernel memory owned by the HCD instance. The important persistent-across-interrupt state includes the idle channel bitmap, channel-to-pipe array, pipe lists, transaction lists, software Tx FIFOs, `frame_number`, `active_split`, cached `usbcx_hprt`, and cached root-hub `port_status`. Endpoint pipe pointers live in `usb_host_endpoint.hcpriv`; URB transaction pointers live in `urb->hcpriv`; ISO temporary packet arrays are temporarily stored in `urb->setup_packet`. There is no filesystem persistence.

Locking is centered on `octeon_hcd.lock`. Completion deliberately drops the spinlock around `usb_hcd_giveback_urb()` and reacquires it afterward. DMA mapping state is delegated to the USB core, except for temporary alignment buffers that are allocated before mapping and restored/freed after unmapping.

## Dependencies and integration points
The file depends on Linux USB HCD APIs, platform devices, OF properties, DMA mapping, IRQ mapping, kernel lists, spinlocks, and OCTEON platform helpers from `<asm/octeon/octeon.h>`. It uses register/unions from `octeon-hcd.h` and OCTEON CSR helpers such as `cvmx_read64_uint32()`, `cvmx_write64_uint32()`, `cvmx_read64_uint64()`, `cvmx_write64_uint64()`, `cvmx_write_csr()`, `cvmx_phys_to_ptr()`, `octeon_get_clock_rate()`, and `OCTEON_IS_MODEL()`.

Device-tree dependencies include a child compatible `cavium,octeon-5750-usbc` and parent USBN `clock-frequency` or `refclk-frequency`, plus `cavium,refclk-type` or `refclk-type`. Hardware integration is tightly tied to OCTEON USBN/USBC register layout and known CN31XX, CN5XXX, CN52XX, and CN56XX errata.

## Risks and edge cases
The driver has high concurrency and hardware-state risk because it maintains its own scheduler, split-transaction state machine, PID toggles, retry policy, and software FIFO handling. Non-DMA mode is especially timing-sensitive: RX FIFO polling must occur quickly enough to avoid overflow, and channel scheduling avoids the final quarter-frame. Split transaction handling uses frame arithmetic, an `active_split` singleton, retry rewinds, and special 188-byte ISO OUT chunks, all of which are regression-prone.

DMA and buffer handling is another risk area. The hardware transfers full 32-bit words, so unaligned-length buffers require temporary bounce buffers unless scatter-gather or pre-mapped DMA is used. ISO uses `urb->setup_packet` as private storage, which is compact but fragile if assumptions about ISO setup usage change. `cvmx_usb_submit_control()` uses setup `wLength` for OUT controls, and mistakes in direction/length interpretation would produce short or overrun transfers.

Error paths sometimes return `-1` instead of a specific errno after initialization/add failures. Probe error handling after successful hardware initialization but failed `usb_add_hcd()` does not call `cvmx_usb_shutdown()`. The interrupt path clears global interrupt status early, so misclassified events may be lost. Root-hub power and suspend semantics are limited; suspend is explicitly unsupported in hub control.

## Test signals
Useful validation includes boot/probe on supported OCTEON models with 12/24/48 MHz reference clocks and both crystal and external clock configurations; device enumeration at high, full, and low speed; full/low-speed devices behind high-speed hubs to exercise split control, bulk, interrupt, and ISO paths; high-speed bulk OUT NAK/PING behavior; unplug/replug and root-hub status change reporting; URB cancellation and endpoint disable while transfers are active; non-DMA CN31XX operation with FIFO interrupts; CN5XXX channel-3 avoidance; and DMA alignment tests with transfer lengths not divisible by four. Kernel dynamic debug around the `dev_dbg()` sites and USB core HCD traces are strong runtime observability signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/octeon-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/octeon-hcd.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/octeon-hcd.h

## Purpose
`octeon-hcd.h` is the hardware register map for the OCTEON USB host driver. It defines the USBC and USBN MMIO address macros plus C bitfield unions used by `octeon-hcd.c` to configure clocks, PHY mode, FIFOs, interrupts, host channels, split transactions, frame timing, port state, DMA-related behavior, and PHY control/status.

## Important APIs, types, and functions
The header exports no callable functions; its API is a set of address macros and typed register layouts. `CVMX_USBCXBASE`, `CVMX_USBCXREG1()`, and `CVMX_USBCXREG2()` derive USBC register addresses by block id and channel offset. `CVMX_USBNXREG1()` and `CVMX_USBNXREG2()` derive USBN control and DMA pointer addresses. Named register macros include global/core registers such as `CVMX_USBCX_GAHBCFG`, `GINTMSK`, `GINTSTS`, `GUSBCFG`, `GRSTCTL`, FIFO registers, host-channel registers such as `HCCHARX`, `HCINTX`, `HCINTMSKX`, `HCSPLTX`, `HCTSIZX`, frame/port registers, and USBN `CLK_CTL`, `DMA0_INB_CHN0`, `DMA0_OUTB_CHN0`, and `USBP_CTL_STATUS`.

Register unions include `cvmx_usbcx_gahbcfg`, `cvmx_usbcx_ghwcfg3`, `cvmx_usbcx_gintmsk`, `cvmx_usbcx_gintsts`, `cvmx_usbcx_gnptxfsiz`, `cvmx_usbcx_gnptxsts`, `cvmx_usbcx_grstctl`, `cvmx_usbcx_grxfsiz`, `cvmx_usbcx_grxstsph`, `cvmx_usbcx_gusbcfg`, `cvmx_usbcx_haint`, `cvmx_usbcx_haintmsk`, `cvmx_usbcx_hccharx`, `cvmx_usbcx_hcfg`, `cvmx_usbcx_hcintx`, `cvmx_usbcx_hcintmskx`, `cvmx_usbcx_hcspltx`, `cvmx_usbcx_hctsizx`, `cvmx_usbcx_hfir`, `cvmx_usbcx_hfnum`, `cvmx_usbcx_hprt`, `cvmx_usbcx_hptxfsiz`, `cvmx_usbcx_hptxsts`, `cvmx_usbnx_clk_ctl`, and `cvmx_usbnx_usbp_ctl_status`.

## Control flow
This header does not execute control flow, but it directly shapes the control flow in `octeon-hcd.c`. Initialization writes `cvmx_usbnx_clk_ctl` and `cvmx_usbnx_usbp_ctl_status` to bring the PHY/core out of reset, programs `cvmx_usbcx_gahbcfg`, `cvmx_usbcx_gusbcfg`, `cvmx_usbcx_gintmsk`, `cvmx_usbcx_hcfg`, and FIFO sizing registers, and then uses host-channel unions for per-transfer setup. Interrupt control flow reads `cvmx_usbcx_gintsts`, `cvmx_usbcx_haint`, and `cvmx_usbcx_hcintx`; transfer accounting reads `cvmx_usbcx_hctsizx` and `cvmx_usbcx_hccharx`; root-hub behavior reads and writes `cvmx_usbcx_hprt`.

## State and persistence behavior
The unions are transient views over MMIO register values. They do not store persistent software state; persistence lives in hardware registers and the driver state in `octeon-hcd.c`. The `__BITFIELD_FIELD` layout is architecture-sensitive and represents the on-chip bit order expected by OCTEON. Address macros are deterministic from block id and channel id.

## Dependencies and integration points
The header depends on `<asm/bitfield.h>` for bitfield declarations and on OCTEON address translation through `CVMX_ADD_IO_SEG`, which is supplied elsewhere in the OCTEON platform headers. Its sole in-tree consumer in this work item is `octeon-hcd.c`, but the register names mirror the OCTEON USB core documentation and the DWC OTG-style host register model.

## Risks and edge cases
The main risks are bitfield layout correctness, 32-bit versus 64-bit register access width, block-id address selection, and channel offset calculations. A single incorrect field width or reserved-bit placement can cause writes to affect unrelated hardware controls. Several comments document fields that must only change during reset or before normal operation; driver changes must preserve those sequencing constraints. Endianness-related fields such as `usbc_end` and the C bitfield ordering make cross-architecture reuse unsafe without platform validation.

## Test signals
Compilation of `octeon-hcd.c` is the first signal because all field names are exercised through these unions. Runtime signals include successful PHY/core reset, valid FIFO depth reads from `GHWCFG3`, correct interrupt masks, working host-channel interrupts, correct port-speed reporting from `HPRT`, and stable DMA pointer behavior through USBN DMA registers. Hardware register dump comparison against vendor documentation is the most direct validation for address and field layout changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/octeon-hcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-at91.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-at91.c

## Purpose
`ohci-at91.c` is the Atmel/Microchip AT91 platform glue for the generic OHCI USB host driver. It supplies clock control, platform data derived from device tree, per-port VBUS GPIO control, optional overcurrent GPIO handling, AT91-specific port suspend through SMC or SFR regmap, and HCD hook overrides for root-hub status/control.

## Important APIs, types, and functions
`struct at91_usbh_data` stores VBUS GPIOs, overcurrent GPIOs, root-hub port count, and per-port overcurrent status/change bits. `struct ohci_at91_priv` is OHCI private extension data containing interface/function/AHB clocks, `clocked`, saved wakeup state, optional SFR regmap, and optional suspend SMC id. `ohci_at91_drv_overrides` sets `.extra_priv_size`.

Clock and controller helpers are `at91_start_clock()`, `at91_stop_clock()`, `at91_start_hc()`, and `at91_stop_hc()`. Probe/remove are split between `usb_hcd_at91_probe()`/`usb_hcd_at91_remove()` and platform-driver wrappers `ohci_hcd_at91_drv_probe()`/`ohci_hcd_at91_drv_remove()`. Hub overrides are `ohci_at91_hub_status_data()` and `ohci_at91_hub_control()`. Suspend support uses `at91_dt_suspend_smc()`, `at91_dt_syscon_sfr()`, `ohci_at91_port_suspend()`, `ohci_hcd_at91_drv_suspend()`, and `ohci_hcd_at91_drv_resume()`. `ohci_hcd_at91_overcurrent_irq()` is the GPIO overcurrent ISR.

## Control flow
Module init calls `ohci_init_driver()`, then overwrites the generated OHCI HCD driver's `hub_status_data` and `hub_control` callbacks before registering the platform driver. Platform probe coerces a 32-bit DMA mask, allocates and attaches `at91_usbh_data`, reads `num-ports`, acquires indexed optional `atmel,vbus` GPIOs as output-high, acquires indexed optional `atmel,oc` GPIOs as inputs, requests shared overcurrent IRQs, enables wakeup, then calls `usb_hcd_at91_probe()`.

`usb_hcd_at91_probe()` allocates the HCD, maps registers, gets `ohci_clk`, `uhpck`, and `hclk`, discovers the suspend control path, sets `ohci->num_ports`, starts clocks and holds the controller in reset, sets `OHCI_CTRL_RWC`, and calls `usb_add_hcd()`. Removal unregisters the HCD, shuts down the controller, disables clocks, turns off VBUS GPIOs, and drops wakeup.

Hub control intercepts Set/ClearPortFeature POWER to toggle per-port VBUS GPIOs, Set/ClearPortFeature SUSPEND to call AT91-specific SFR/SMC suspend control, and overcurrent clear requests to update software flags. Other requests are delegated to `ohci_hub_control()`, then GetHubDescriptor is patched to advertise individual power switching and optional individual overcurrent protection, and GetPortStatus is patched to reflect GPIO power and software overcurrent bits.

System suspend saves whether wakeup is allowed outside slow-clock mode, enables IRQ wake when needed, calls `ohci_suspend()`, then either halts root-hub state and stops clocks or leaves clocks active for wake while asserting AT91 port suspend. Resume clears port suspend, disables IRQ wake or restarts clocks, and calls `ohci_resume()` with reset requested when clocks were stopped.

## State and persistence behavior
State is in device-managed GPIO/clock/regmap resources, `pdev->dev.platform_data`, OHCI private memory, and the OHCI core. `overcurrent_status[]` and `overcurrent_changed[]` are software latched status exposed through root-hub status and cleared through hub feature requests. `clocked` prevents duplicate clock enable/disable operations. `wakeup` persists only across suspend/resume.

## Dependencies and integration points
The driver depends on the generic OHCI core (`ohci.h`, `ohci_init_driver()`, `ohci_setup` through generic start, `ohci_hub_control()`, `ohci_hub_status_data()`, `ohci_suspend()`, `ohci_resume()`), Linux clock, GPIO descriptor, platform device, OF, DMA, regmap/syscon, ARM SMCCC, and AT91 SFR APIs. Device-tree bindings include `atmel,at91rm9200-ohci`, `num-ports`, indexed `atmel,vbus`, indexed `atmel,oc`, and optional `microchip,suspend-smc-id`; SFR fallback matches `atmel,sama5d2-sfr` or `microchip,sam9x60-sfr`.

## Risks and edge cases
`pdata->ports` defaults to zero if `num-ports` is absent, which would register an OHCI controller with no platform-described ports. VBUS GPIO acquisition errors are logged but do not fail probe, so missing power control may surface later as dead ports. Overcurrent IRQ setup failures are informational and overcurrent protection may be absent. The ISR only latches active-low overcurrent notification and does not explicitly clear status on exit; user-visible clearing depends on hub feature requests. Suspend behavior depends on slow-clock mode and on either SMC or SFR regmap availability; errors from `ohci_at91_port_suspend()` are ignored in some hub-control/suspend paths.

## Test signals
Test with AT91 device trees covering one to three ports, with and without VBUS GPIOs, with and without overcurrent GPIOs, and with SMC versus SFR suspend paths. Observe root-hub descriptors for individual power/overcurrent flags, per-port power changes through hub requests, overcurrent IRQ latching and clearing through `C_OVER_CURRENT`, system suspend/resume both with wakeup enabled and with clocks stopped, and regression against generic OHCI enumeration for low/full-speed devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-at91.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-da8xx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-da8xx.c

## Purpose
`ohci-da8xx.c` is the TI DA8xx/OMAP-L1x platform glue for the generic OHCI host driver. It powers and clocks the USB1.1 OHCI block, integrates a PHY, optionally controls VBUS through a regulator, reports overcurrent through either a GPIO or regulator error flags, and overrides root-hub callbacks so the one real external port is represented correctly.

## Important APIs, types, and functions
`struct da8xx_ohci_hcd` extends OHCI private data with the HCD pointer, USB1.1 clock, PHY, optional VBUS regulator, regulator notifier, and optional overcurrent GPIO. `ocic_mask` is a global volatile bitmask for overcurrent-indicator-change reporting. `da8xx_overrides` sets `.reset = ohci_da8xx_reset` and `.extra_priv_size`.

Resource/power helpers are `ohci_da8xx_enable()`, `ohci_da8xx_disable()`, `ohci_da8xx_set_power()`, `ohci_da8xx_get_power()`, `ohci_da8xx_get_oci()`, `ohci_da8xx_has_set_power()`, and `ohci_da8xx_has_oci()`. Overcurrent callbacks are `ohci_da8xx_regulator_event()`, `ohci_da8xx_oc_thread()`, and `ohci_da8xx_register_notify()`. OHCI integration is via `ohci_da8xx_reset()`, `ohci_da8xx_hub_status_data()`, `ohci_da8xx_hub_control()`, `ohci_da8xx_probe()`, `ohci_da8xx_remove()`, optional suspend/resume, and module init/exit.

## Control flow
Module init initializes a generic OHCI driver with DA8xx reset/private overrides, saves the generic `hub_control` and `hub_status_data` callbacks, replaces them with DA8xx wrappers, and registers the platform driver. Probe allocates the HCD, gets the clock and `"usb-phy"`, optionally gets a `"vbus"` regulator, optionally gets an `"oc"` GPIO and threaded IRQ, maps registers, gets the main IRQ, calls `usb_add_hcd()`, enables wakeup, and registers a regulator overcurrent notifier if applicable.

During OHCI reset, `ohci_da8xx_enable()` enables the clock, initializes the PHY, powers it on, forces `ohci->num_ports = 1` because the hardware root-hub register reports two ports, calls `ohci_setup()`, and patches root hub register A to advertise per-port power switching and overcurrent support when the platform has those capabilities.

Hub status wraps the original OHCI status bitmap and adds port 1 status-change notification if `ocic_mask` is set. Hub control intercepts GetPortStatus for port 1 to combine generic `roothub_portstatus()` with regulator/GPIO power and overcurrent state, and intercepts Set/ClearPortFeature POWER and C_OVER_CURRENT. Everything else delegates to the original OHCI callback.

Suspend waits for OHCI state-change timing, calls `ohci_suspend()`, disables PHY/clock, and marks the HCD suspended. Resume reenables clock/PHY and calls `ohci_resume()`.

## State and persistence behavior
Private HCD state is per-controller. `ocic_mask` is file-global, not per-controller, which is acceptable only if one controller/port is expected. VBUS regulator state persists in regulator framework state; PHY/clock state is controlled through runtime calls. The overcurrent change bit remains latched in `ocic_mask` until a ClearPortFeature C_OVER_CURRENT hub request clears it.

## Dependencies and integration points
This file depends on generic OHCI internals (`ohci.h`, `ohci_setup()`, `ohci_init_driver()`, root-hub helpers, suspend/resume), platform device resources, Linux clock, PHY, regulator, GPIO descriptor, threaded IRQs, jiffies timing, unaligned access helpers, and OF matching for `ti,da830-ohci`.

## Risks and edge cases
The global `ocic_mask` is not protected by a lock and is shared across potential instances. Regulator and GPIO overcurrent paths have different polarity/semantics: the GPIO thread disables the regulator when the GPIO reads asserted and a regulator exists, while `ohci_da8xx_get_oci()` reports GPIO value directly. If platform polarity is misdescribed, root-hub overcurrent reporting and VBUS shutdown can invert. Probe registers the regulator notifier after `usb_add_hcd()`, so an early overcurrent event during registration window may be missed. Suspend/resume manually rate-limits around `ohci->next_statechange`; missed timing can affect OHCI state transitions.

## Test signals
Validate enumeration on DA8xx with only the mandatory clock/PHY, with a VBUS regulator, with an overcurrent GPIO, and with regulator overcurrent events. Check that the root hub advertises one port, Set/ClearPortFeature POWER toggles VBUS, overcurrent sets OCIC and disables VBUS, ClearPortFeature C_OVER_CURRENT clears `ocic_mask`, and suspend/resume restores enumeration. Inspect `roothub.a` behavior after reset to confirm power/OCI capability bits match platform resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-da8xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-dbg.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-dbg.c

## Purpose
`ohci-dbg.c` provides debug logging and debugfs snapshots for the generic OHCI host driver. It formats controller registers, root-hub status, endpoint descriptors, transfer descriptors, asynchronous schedules, periodic schedules, and frame timing into either kernel debug logs or per-controller debugfs files.

## Important APIs, types, and functions
Formatting macros include `edstring()`, `pipestring()`, `ohci_dbg_sw()`, `ohci_dbg_nosw()`, and `dbg_port_sw()`. Register and state dump helpers include `ohci_dump_intr_mask()`, `maybe_print_eds()`, `hcfs2string()`, `rh_state_string()`, `ohci_dump_status()`, `ohci_dump_roothub()`, and `ohci_dump()`. Descriptor dump helpers are `ohci_dump_td()` and `ohci_dump_ed()`.

Debugfs support uses `struct debug_buffer`, file operations for `async`, `periodic`, and `registers`, and helpers `show_list()`, `fill_async_buffer()`, `fill_periodic_buffer()`, `fill_registers_buffer()`, `alloc_buffer()`, `fill_buffer()`, `debug_output()`, `debug_close()`, `debug_async_open()`, `debug_periodic_open()`, `debug_registers_open()`, `create_debug_files()`, and `remove_debug_files()`. The file also uses the global `ohci_debug_root` dentry as the parent directory for per-bus debug directories.

## Control flow
Debug dumping is demand-driven. Kernel logging paths call `ohci_dump()`, `ohci_dump_td()`, or `ohci_dump_ed()` directly. Debugfs open allocates a small `debug_buffer` bound to the selected fill function and stores it in `file->private_data`. The first read calls `fill_buffer()`, which lazily allocates one zeroed page and invokes the fill function. Subsequent reads use `simple_read_from_buffer()` over the cached page until close frees it.

`fill_async_buffer()` locks `ohci->lock` and dumps the control and bulk ED chains through `show_list()`. `fill_periodic_buffer()` allocates a bounded `seen` array, locks the OHCI state, walks `NUM_INTS` periodic slots, prints load and ED metadata, and avoids expanding duplicate ED chains beyond the first observation. `fill_registers_buffer()` locks OHCI state, prints bus/device/driver identity, skips MMIO reads when `HCD_HW_ACCESSIBLE()` is false, then dumps status, HCCA frame, frame interval/remaining/threshold registers, hub-poll state, and root-hub registers.

## State and persistence behavior
Debug output is a snapshot, not live streaming. Each open debugfs file has one `struct debug_buffer`, one mutex, an optional allocated page, and a byte count. Hardware/software state is read under the OHCI spinlock where needed. The debugfs directory pointer is stored in `ohci->debug_dir` and removed recursively by `remove_debug_files()`. No data persists beyond the file lifetime.

## Dependencies and integration points
The file is meant to be included by or compiled with the OHCI core context and relies on `ohci.h` internals: `struct ohci_hcd`, `struct ohci_regs`, ED/TD layouts, root-hub helper macros, `ohci_readl()`, `ohci_frame_no()`, `ohci_to_hcd()`, `hc32_to_cpu()`, `hc32_to_cpup()`, and debug/logging macros. It depends on debugfs, file operations, mutexes, spinlocks, page allocation, and user-copy read helpers.

## Risks and edge cases
All debugfs fill functions are page-sized; large schedules can be truncated by `scnprintf()` size exhaustion. The periodic debug path limits duplicate ED tracking to `DBG_SCHED_LIMIT` entries, so complex schedules may omit repeated chain expansion. Some helpers print kernel pointers, which is acceptable for debug builds but sensitive from an information-disclosure perspective depending on debugfs permissions and pointer hashing configuration. Register reads are skipped when hardware is inaccessible, but async/periodic schedule dumps still depend on coherent in-memory OHCI structures.

## Test signals
With OHCI debugfs enabled, each controller should create `async`, `periodic`, and `registers` files under its bus directory. Reading them while idle, under bulk/control traffic, and under interrupt/ISO periodic traffic should produce coherent ED/TD chains and register snapshots without lock warnings, sleeping-in-atomic reports, or page overflows. Suspend reads should show the explicit inaccessible-hardware message in `registers` instead of faulting on MMIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-exynos.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-exynos.c

## Purpose
`ohci-exynos.c` is Samsung Exynos platform glue for the generic OHCI USB host driver. It handles DMA-mask setup, HCD allocation, PHY discovery using current or legacy device-tree bindings, USB host clock management, PHY power sequencing, legacy OF-node masking, suspend/resume, and platform-driver registration.

## Important APIs, types, and functions
`struct exynos_ohci_hcd` stores the USB host clock, original OF node, up to three PHY handles, and a `legacy_phy` flag. `PHY_NUMBER` caps supported PHYs at three. Main helpers are `exynos_ohci_get_phy()`, `exynos_ohci_phy_enable()`, `exynos_ohci_phy_disable()`, `exynos_ohci_probe()`, `exynos_ohci_remove()`, `exynos_ohci_shutdown()`, `exynos_ohci_suspend()`, and `exynos_ohci_resume()`. `exynos_overrides` only supplies OHCI private data size; core OHCI reset/setup behavior is otherwise generic.

## Control flow
Probe coerces a 32-bit DMA mask, allocates an HCD with `exynos_ohci_hc_driver`, gets PHYs, obtains and enables the `"usbhost"` clock via `devm_clk_get_enabled()`, maps the MMIO resource, retrieves the IRQ, stores the HCD in platform drvdata, powers on all PHYs, optionally hides `pdev->dev.of_node` for legacy PHY subnode bindings, calls `usb_add_hcd()` with `IRQF_SHARED`, and enables wakeup.

PHY discovery first counts `phys` phandles with `#phy-cells` and gets each by index. If no modern PHY phandles exist, it iterates available child nodes, reads each child `reg` as the PHY slot, gets an optional PHY from that child, and marks `legacy_phy = true`. PHY enable powers on each stored PHY in order and unwinds previously powered PHYs on failure. PHY disable powers off all slots.

Removal restores the original OF node, removes the HCD, powers off PHYs, and releases the HCD. Shutdown delegates to the HCD driver's shutdown callback. Suspend calls `ohci_suspend()`, disables PHYs, and disables the clock. Resume reenables the clock, powers PHYs, unwinds clock on PHY failure, and calls `ohci_resume()`.

## State and persistence behavior
State is per-HCD private data plus device-managed clock/PHY/MMIO resources. `of_node` stores the original platform OF node so the probe-time legacy workaround can be undone on remove or add failure. There is no persistent state. Wakeup enablement is set after successful add and consulted during suspend through `device_may_wakeup()`.

## Dependencies and integration points
The driver depends on the generic OHCI core, Linux platform device, OF, PHY, clock, DMA, and USB HCD APIs. It matches `samsung,exynos4210-ohci`. The legacy binding behavior is an integration point with older Exynos device trees where PHYs are child nodes that could otherwise be mistaken for generic USB device child nodes.

## Risks and edge cases
`exynos_ohci_get_phy()` does not explicitly bound `num_phys` from modern `phys` phandles against `PHY_NUMBER`, so a device tree with more than three PHYs could write past `phy[]`. The legacy path does validate child `reg` against `PHY_NUMBER`. `phy_power_on(NULL)` behavior depends on the PHY API tolerating optional NULL handles; the code assumes unused slots are safe. Suspend disables a clock acquired through `devm_clk_get_enabled()`, then resume manually prepares/enables it, which is valid but requires balanced PM paths. The temporary `of_node = NULL` legacy workaround must be restored on every failure/removal path; the code restores it after `usb_add_hcd()` failure and in remove.

## Test signals
Validate modern `phys` bindings with one to three PHYs, legacy child-node PHY bindings, and no optional legacy PHY for unused slots. Probe should map MMIO, share IRQ, enumerate USB devices, and not create bogus USB child devices from legacy PHY child nodes. Suspend/resume should power-cycle PHYs and clock cleanly while preserving enumeration after resume. A negative DT test with too many modern PHYs is valuable because the array bound is not guarded in that path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ohci-exynos.c -->
