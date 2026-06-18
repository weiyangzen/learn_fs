# Research: subset-b-005525

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-tegra-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-tegra-usb.c

## Purpose
This file is the legacy `usb_phy` provider for NVIDIA Tegra20/Tegra30 USB PHY blocks. It supports three interface modes selected from DT: UTMI, ULPI, and HSIC. It programs PHY timing, PLL, pad, VBUS wake, PMC always-on detector, and controller-side PORTSC/HOSTPC USB mode bits, then registers a `struct usb_phy` through `usb_add_phy_dev()`.

## Important APIs, Types, And Functions
The driver centers on `struct tegra_usb_phy` and SoC-specific `struct tegra_phy_soc_config`. The `tegra_freq_table` maps PLL parent rates to hardware delay/count fields. Public integration is via `u_phy.init = tegra_usb_phy_init`, `shutdown = tegra_usb_phy_shutdown`, `set_wakeup = tegra_usb_phy_set_wakeup`, and `set_suspend = tegra_usb_phy_set_suspend`.

UTMI helpers include `utmip_pad_open/close()`, `utmip_pad_power_on/off()`, `utmi_phy_clk_enable/disable()`, and `utmi_phy_power_on/off()`. ULPI paths use `ulpi_phy_power_on/off()` plus the generic `devm_otg_ulpi_create()` object and `ulpi_viewport_access_ops`. HSIC paths use `uhsic_phy_power_on/off()` and SoC offset/value fields. Probe helpers parse DT tuning (`read_utmi_param()`, `utmi_phy_probe()`), PMC phandles (`tegra_usb_phy_parse_pmc()`), clocks, resets, regulators, reset GPIOs, and MMIO resources.

## Control Flow
Probe allocates state, maps controller/PHY registers without claiming them exclusively because the USB controller shares the MMIO window, reads `dr_mode`, obtains `vbus` and `pll_u`, optionally gets PMC regmap, then initializes the selected PHY type. Runtime users call `usb_phy_init()`, which enables `pll_u`, picks a frequency profile, enables VBUS, opens UTMI pads if needed, configures PMC wake detectors, and powers on the selected PHY. Suspend calls power-off and resume calls power-on under shared IRQ masking. Shutdown disables wakeup, powers off, closes UTMI pads, disables regulator and PLL, and clears `freq`.

## State And Persistence
Persistent state is in the platform device driver data: mapped registers, clocks, resets, regulator, PHY mode, `powered_on`, `wakeup_enabled`, `freq`, `pad_wakeup`, and optional PMC regmap/instance. A global `utmip_pad_count` protected by `utmip_pad_lock` reference-counts shared UTMI bias/pad power across ports. Hardware state persists in PHY/PMC registers until power/reset changes.

## Dependencies And Integration Points
The driver depends on OF properties such as `phy_type`, `dr_mode`, `nvidia,*` UTMI timing fields, optional `nvidia,pmc`, `nvidia,has-legacy-mode`, clocks (`pll_u`, `utmi-pads`, `ulpi-link`), resets (`utmi-pads`), a VBUS regulator, and ULPI reset GPIO. It integrates with the legacy USB PHY API, regulator, reset, clk, regmap, GPIO, and the Tegra USB controller through shared register programming.

## Risks
Shared registers and shared IRQs create race risk; `tegra_usb_phy_set_suspend()` masks IRQs while reprogramming because the controller interrupt path can touch the same registers. UTMI pad refcount bugs can leave common bias powered off while another port uses it, or powered on during suspend. Wakeup differs by mode; ULPI wakeup is explicitly unsupported and returns `-EOPNOTSUPP` if requested. DT tuning values are mandatory for UTMI/HSIC and invalid PLL parent rates fail init. Error unwinding must keep `pll_u`, VBUS, and UTMI pads balanced.

## Test Signals
Exercise probe deferral for PMC/regulator/clock/reset dependencies, all three PHY modes, valid/invalid DT tuning, parent PLL rates, suspend/resume with wake enabled and disabled, device/host/OTG `dr_mode`, shared IRQ wake interrupts, and repeated init/shutdown cycles to catch UTMI pad count imbalance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-tegra-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-twl6030-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-twl6030-usb.c

## Purpose
This file implements the TWL6030 USB transceiver/companion glue for OMAP MUSB. It talks to TWL I2C register banks to detect VBUS and ID changes, control the TWL USB LDO and charge-pump VBUS drive, and publish status to MUSB through `musb_mailbox()` and `omap_usb2_set_comparator()`.

## Important APIs, Types, And Functions
`struct twl6030_usb` stores the `phy_companion`, device, spinlock, `usb3v3` regulator, two IRQs, delayed cable-status work, VBUS-setting work, current `linkstat`, `asleep`, and `vbus_enable`. Register helpers `twl6030_writeb()` and `twl6030_readb()` wrap TWL I2C access with logging. `twl6030_start_srp()` pulses VBUS control registers for SRP; `twl6030_set_vbus()` schedules `otg_set_vbus_work()` to write `CHARGERUSB_CTRL1`.

The two IRQ handlers split events: `twl6030_usb_irq()` handles VBUS detection using `STS_HW_CONDITIONS` and charger controller status, while `twl6030_usbotg_irq()` handles USB ID transitions. `vbus_show()` exposes `"vbus"`, `"id"`, `"none"`, or `"UNKNOWN"` through sysfs.

## Control Flow
Probe requires DT, allocates `twl6030_usb`, fetches two IRQs, installs comparator callbacks, defers if the OMAP USB2 PHY is not ready, initializes the LDO/regulator and TWL comparator bits, requests both threaded IRQs, unmasks TWL interrupt sources, and schedules delayed initial status sampling. IRQs update `linkstat`, enable or disable `usb3v3`, call `musb_mailbox()`, and notify sysfs. Remove cancels delayed/current work, masks interrupts, frees IRQs, and releases the regulator.

## State And Persistence
Driver-visible state is `linkstat`, `asleep`, `vbus_enable`, and the regulator enable state. Hardware state persists in TWL ID/USB/charger register banks. The workqueue paths allow VBUS drive from atomic contexts without direct I2C writes.

## Dependencies And Integration Points
The file depends on TWL MFD I2C APIs, TWL interrupt mask helpers, regulator core, MUSB mailbox statuses, OMAP USB PHY comparator registration, platform IRQ resources, and the `ti,twl6030-usb` compatible. It is registered at `subsys_initcall` so it is available early for MUSB/PHY wiring.

## Risks
The sysfs reader uses `twl->lock`, but IRQ handlers update `linkstat` without taking it, so status reads are best-effort. `twl6030_readb()` returns a `u8` even though it may carry negative errors via an `int`, which can hide I2C failures in event logic. Regulator enable/disable is tied to `asleep` and mailbox success; failures can leave state as `MUSB_UNKNOWN`. Work and IRQ teardown order matters because delayed work calls the IRQ handlers directly.

## Test Signals
Test VBUS attach/detach, ID-ground transitions, regulator failures, MUSB mailbox failures, sysfs `vbus` output, SRP and VBUS drive callbacks, probe deferral from `omap_usb2_set_comparator()`, and remove while delayed status work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-twl6030-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ulpi-viewport.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ulpi-viewport.c

## Purpose
This small file provides a generic ULPI viewport access backend for controllers that expose ULPI registers through a memory-mapped viewport register. It exports `ulpi_viewport_access_ops` as `struct usb_phy_io_ops`.

## Important APIs, Types, And Functions
The main operations are `ulpi_viewport_read()` and `ulpi_viewport_write()`. Both first write `ULPI_VIEW_WAKEUP | ULPI_VIEW_WRITE`, wait for `ULPI_VIEW_WAKEUP` to clear through `ulpi_viewport_wait()`, then issue a `ULPI_VIEW_RUN` transaction with read/write mode, address, and write data. Reads return `ULPI_VIEW_DATA_READ(readl(view))`; writes return only transaction completion status.

## Control Flow
Users set `usb_phy->io_priv` to the viewport MMIO address and `usb_phy->io_ops` to `ulpi_viewport_access_ops`. The generic ULPI code then calls these methods for register reads/writes. Each transaction is synchronous and uses atomic polling with a 2 ms timeout.

## State And Persistence
No private software state is stored in this file. The only persistent state is controller hardware viewport contents and the caller-owned `io_priv` pointer.

## Dependencies And Integration Points
It depends on Linux MMIO helpers, `readl_poll_timeout_atomic()`, and the legacy `usb_phy` I/O abstraction. Tegra ULPI uses it by assigning `tegra_phy->ulpi->io_priv = regs + ULPI_VIEWPORT`.

## Risks
Timeouts propagate as negative errors to the caller; callers must not assume a ULPI register value if read returns a negative code. Because the helper uses atomic polling, it is suitable for locked paths but can still spin for up to 2 ms per transaction. Incorrect `io_priv` mapping or controller-specific viewport layout mismatch will corrupt unrelated MMIO.

## Test Signals
Use ULPI scratch read/write integrity checks through the generic ULPI layer, inject stuck `WAKEUP` or `RUN` bits, verify timeout propagation, and validate byte address/data packing against controller documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ulpi-viewport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ulpi.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ulpi.c

## Purpose
This file is generic support for legacy ULPI USB transceivers. It creates a `struct usb_phy`/`struct usb_otg` pair, probes vendor/product IDs, checks the ULPI scratch register, programs OTG/function/interface control bits from `phy->flags`, and provides OTG host/VBUS callbacks.

## Important APIs, Types, And Functions
`devm_otg_ulpi_create()` allocates the managed PHY and OTG objects and initializes them through `otg_ulpi_init()`. `ulpi_init()` reads the four ID bytes, logs known transceivers from `ulpi_ids`, runs `ulpi_check_integrity()`, and calls `ulpi_set_flags()`. Flag programming is split into `ulpi_set_otg_flags()`, `ulpi_set_fc_flags()`, and `ulpi_set_ic_flags()`. OTG callbacks are `ulpi_set_host()` and `ulpi_set_vbus()`.

## Control Flow
A controller driver supplies `struct usb_phy_io_ops`, flags, and later an `io_priv` backend. On PHY init, the generic code uses `usb_phy_io_read/write()` for all ULPI register access. Host assignment updates `otg->host` and serial/carkit bits. VBUS assignment updates `DRVVBUS` and `DRVVBUS_EXT` depending on configured flags.

## State And Persistence
Software state is the managed `usb_phy`, `usb_otg`, `phy->flags`, `phy->io_ops`, and `otg->host`. Hardware state lives in the ULPI OTG, function-control, interface-control, and scratch registers.

## Dependencies And Integration Points
The file integrates with legacy `usb_phy`, `usb_otg`, and controller-specific ULPI I/O providers such as the viewport backend. It is used by platform PHY drivers that want generic ULPI enumeration and OTG behavior without implementing register policy themselves.

## Risks
`ulpi_set_host()` and `ulpi_set_vbus()` assign the result of `usb_phy_io_read()` to an unsigned value before testing write behavior; a negative read error can be transformed into a large bit pattern. Scratch-register integrity is the main sanity check, so broken I/O callbacks can fail init. Flag combinations can produce invalid electrical or serial modes if platform data is wrong.

## Test Signals
Exercise known and unknown ULPI IDs, scratch integrity failure, each OTG/FC/IC flag combination used by boards, VBUS on/off transitions, host attach/detach, and error propagation from controller `io_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ulpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy.c

## Purpose
This file implements the legacy USB PHY registry and charger-notification support. It lets providers register `struct usb_phy` objects, lets host/peripheral/charger drivers acquire them by type, OF node, or phandle, and emits charger current/state changes through atomic notifiers and uevents.

## Important APIs, Types, And Functions
The exported provider APIs are `usb_add_phy()`, `usb_add_phy_dev()`, `usb_remove_phy()`, and `usb_phy_set_event()`. Consumer APIs are `usb_get_phy()`, `devm_usb_get_phy()`, `devm_usb_get_phy_by_node()`, `devm_usb_get_phy_by_phandle()`, and `usb_put_phy()`. Charger APIs include `usb_phy_set_charger_current()`, `usb_phy_get_charger_current()`, and `usb_phy_set_charger_state()`.

Internally, `phy_list` and `phy_lock` protect global PHY enumeration. `usb_charger_init()` initializes default current ranges and work; `usb_add_extcon()` wires extcon notifiers for VBUS/ID or charger type detection. `usb_phy_notify_charger_work()` calls notifier chains and emits `KOBJ_CHANGE`; `usb_phy_uevent()` adds `USB_CHARGER_STATE` and `USB_CHARGER_TYPE`.

## Control Flow
Providers initialize a `struct usb_phy`, then call `usb_add_phy()` for a unique type or `usb_add_phy_dev()` for device-based registration. Consumers acquire a reference under `phy_lock`; successful acquisition increments both module and device refs. Extcon state changes update `chg_type`/`chg_state` and schedule work. Removal deletes the PHY from the list; devm release unregisters optional notifiers and puts refs.

## State And Persistence
State is in the global list, each PHY's device type, charger current limits, charger type/state, notifier head, extcon devices, and pending work. This is in-memory kernel state only; hardware state is owned by concrete PHY drivers.

## Dependencies And Integration Points
It depends on Linux device, module, OF, extcon, notifier, workqueue, and kobject uevent infrastructure. Concrete providers such as the Tegra PHY register here; gadget/host code can retrieve legacy PHYs or subscribe to charger events.

## Risks
This is a global singleton-style registry for typed PHYs, so duplicate `usb_add_phy()` types return `-EBUSY`. The list is protected by a spinlock, but notifier registration and charger work rely on provider lifetime discipline. `usb_add_phy_dev()` sets `x->dev->type`, which affects device uevents globally. Extcon absence or partial extcon phandle sets changes whether charger type or VBUS/ID notifiers are installed.

## Test Signals
Test duplicate type registration, probe deferral by OF node before provider registration, devm release paths, module refcount failure, extcon charger attach/detach for SDP/CDP/DCP/ACA, current clamping, and uevent contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/Kconfig

## Purpose
This Kconfig entry exposes the Renesas USBHS controller driver as `CONFIG_USB_RENESAS_USBHS`.

## Important APIs, Types, And Functions
The file defines one tristate symbol, `USB_RENESAS_USBHS`, with the prompt "Renesas USBHS controller". It has no C APIs or runtime state.

## Control Flow
The symbol can be built in, modular, or disabled. Its help text describes a full/high-speed USB 2.0 controller with endpoint zero and nine or more configurable endpoints, producing a `renesas_usbhs` module when built as `m`.

## State And Persistence
Configuration persists in the kernel build `.config` and controls Makefile object inclusion. No runtime state is stored here.

## Dependencies And Integration Points
The symbol depends on `USB_GADGET`, platform reachability (`ARCH_RENESAS || SUPERH || COMPILE_TEST`), and `EXTCON || !EXTCON` to prevent a built-in USBHS driver from depending on modular extcon. Host and gadget subcomponents are included by related `CONFIG_USB_RENESAS_USBHS_HCD` and `CONFIG_USB_RENESAS_USBHS_UDC` checks in the Makefile/header guards.

## Risks
The top-level driver depends on `USB_GADGET`, even though it can include host mode support, so host-only configurations must still satisfy gadget-side dependencies. The extcon dependency is subtle and prevents build/link ordering problems when extcon is modular.

## Test Signals
Build test `y`, `m`, and disabled combinations, plus `COMPILE_TEST` without Renesas/SuperH. Validate host/gadget object inclusion combinations and the extcon built-in/module matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/Makefile

## Purpose
This Makefile builds the composite `renesas_usbhs.o` driver and conditionally links host and gadget frontends.

## Important APIs, Types, And Functions
The base object list is `common.o mod.o pipe.o fifo.o rcar2.o rcar3.o rza.o rza2.o`. `mod_host.o` is appended when `CONFIG_USB_RENESAS_USBHS_HCD` is non-empty, and `mod_gadget.o` is appended when `CONFIG_USB_RENESAS_USBHS_UDC` is non-empty.

## Control Flow
`obj-$(CONFIG_USB_RENESAS_USBHS) += renesas_usbhs.o` selects the composite object. Conditional `ifneq` blocks add frontend modules to the same final object rather than producing separate loadable modules.

## State And Persistence
The file controls build-time composition only. Runtime state is in the C objects it links.

## Dependencies And Integration Points
It mirrors `mod.h` conditional declarations: if a frontend object is not linked, the corresponding probe/remove helpers compile as static stubs. `rza2.o` is part of the linked object even though this work item covers `rza.c`/`rza.h`; `rza.h` declares the additional RZ/A2 and RZ/G2L platform-info exports.

## Risks
Mismatches between Makefile conditions and `mod.h` guards would cause unresolved references or dead frontend stubs. Because all SoC glue objects are always linked with the base driver, their exported platform-info symbols must remain buildable under all supported architectures.

## Test Signals
Build all four combinations of HCD/UDC enabled/disabled under `USB_RENESAS_USBHS=y/m`, and verify `renesas_usbhs.o` contains the expected frontend symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/common.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/common.c

## Purpose
`common.c` is the Renesas USBHS platform driver and shared controller layer. It owns MMIO access, power/clock/reset setup, OF/platform matching, hotplug role switching, runtime power policy, device request helpers, bus reset/SOF helpers, and suspend/resume.

## Important APIs, Types, And Functions
Low-level register helpers are `usbhs_read()`, `usbhs_write()`, and `usbhs_bset()`. System-mode helpers include `usbhs_sys_host_ctrl()`, `usbhs_sys_function_ctrl()`, `usbhs_sys_function_pullup()`, and `usbhs_sys_set_test_mode()`. Control/bus helpers include `usbhs_usbreq_get_val()`, `usbhs_usbreq_set_val()`, `usbhs_bus_send_reset()`, `usbhs_bus_send_sof_enable()`, `usbhs_bus_get_speed()`, `usbhs_vbus_ctrl()`, `usbhs_set_device_config()`, and `usbhs_xxxsts_clear()`.

`usbhs_probe()` allocates `usbhs_priv`, maps registers, copies platform parameters, initializes pipe/FIFO/module layers, deasserts resets, calls SoC callbacks, selects autonomy or non-autonomy hotplug mode, and schedules cold-plug detection. `usbhsc_hotplug()` is the role-selection state machine. `usbhsc_power_ctrl()` combines runtime PM, clocks, platform `power_ctrl`, and `SCKE`.

## Control Flow
Probe resolves `renesas_usbhs_platform_info` from OF or platform data, obtains IRQ, extcon, reset array, clocks, pipe defaults, and optional enable GPIO. It temporarily powers/clocks the hardware to access registers, probes pipe/FIFO/mod subsystems, then drops temporary power and switches to permanent or runtime-controlled mode. Hotplug reads VBUS and ID, checks extcon role agreement if present, changes current mode, powers on, initializes bus registers, and starts host or gadget. On disconnect it stops the mode, reinitializes bus, powers off if runtime controlled, clears mode, and resets the PHY.

## State And Persistence
Persistent state lives in `struct usbhs_priv`: MMIO base, IRQ, callbacks, driver parameters, delayed hotplug work, extcon, spinlock, mod/pipe/FIFO info, generic PHY, reset controls, and clocks. Hardware state includes SYSCFG, DVSTCTR, DEVADDn, interrupt status/enable registers, and SoC glue registers.

## Dependencies And Integration Points
It binds many Renesas compatibles to R-Car Gen2/Gen3, RZ/A, and RZ/G2L platform-info structures. It integrates with the Linux platform driver model, reset, clk, PM runtime, extcon, GPIO, generic PHY through SoC callbacks, and the internal `mod`, `pipe`, and `fifo` subsystems.

## Risks
Power ordering is delicate: probe temporarily enables clocks/PM, later switches to runtime or always-on autonomy mode, and suspend/resume must restore hotplug detection. `usbhsc_power_ctrl()` returns void and can silently abandon enable after a clock failure. Hotplug role mismatch with extcon causes ignored connection. The code assumes platform `get_id` exists. Interrupt teardown explicitly frees the devm IRQ before removing modules to avoid use-after-free.

## Test Signals
Test cold-plug and delayed hotplug, runtime and autonomy power modes, extcon host/gadget mismatch, reset assertion failures, multi-clock DTs with one or two clocks, suspend/resume while connected and disconnected, VBUS control callbacks, and all compatible-to-platform-info matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/common.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/common.h

## Purpose
`common.h` is the shared Renesas USBHS register map, bit-field definition, central private-state declaration, and cross-module function interface.

## Important APIs, Types, And Functions
The header defines register offsets for SYSCFG, DVSTCTR, FIFO registers, interrupt registers, setup packet registers, DCP/PIPE registers, transaction counters, DEVADDn, Gen2 extra DFIFOs, and RZ/A SUSPMODE. It defines bit masks for module enable, host/function selection, pull-up/down, FIFO status, interrupt enable/status, device/control states, pipe transfer types, buffer fields, PID states, DATA toggle control, and device address configuration.

`struct usbhs_priv` aggregates the platform driver's persistent state: MMIO base, IRQ, platform callbacks/parameters, delayed hotplug work, platform device, extcon, spinlock, mode info, pipe info, FIFO info, optional PHY, resets, and up to two clocks. It declares shared functions exported by `common.c` and includes `mod.h` and `pipe.h` so the private state can embed their structures.

## Control Flow
There is no executable control flow in the header, but its macros shape every module's control flow. `usbhs_lock()`/`usbhs_unlock()` wrap the shared spinlock. `usbhs_get_dparam()` gives mutable access to driver parameters copied from platform info.

## State And Persistence
All persistent driver state is represented by `usbhs_priv`. Hardware persistence is represented by the register/bit definitions, especially interrupt status and pipe/FIFO state that survive until explicitly cleared or reset.

## Dependencies And Integration Points
It depends on Linux clk, extcon, platform_device, reset, and `linux/usb/renesas_usbhs.h`. It is included by common, mode, pipe, FIFO, host/gadget, and SoC glue files.

## Risks
The register macros are shared contracts; a wrong bit mask affects multiple modules. `usbhs_get_dparam()` returns an lvalue, and `common.c` mutates copied platform parameters, so callers must know whether they are reading defaults or patched runtime values. Circular inclusion with `mod.h`/`pipe.h` is intentional but fragile.

## Test Signals
Build coverage is the primary signal. Runtime signals include correct interrupt clearing, device-state decoding, pipe PID transitions, FIFO length reads, and DEVADDn configuration across host and gadget paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/fifo.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/fifo.c

## Purpose
`fifo.c` implements Renesas USBHS packet transfer engines over CFIFO/DFIFO using PIO or DMA. It queues `usbhs_pkt` objects on pipes, selects FIFOs, moves data, controls BRDY/BEMP interrupts, maps DMA buffers, handles DMA completion, and initializes FIFO resources.

## Important APIs, Types, And Functions
Public entry points are `usbhs_pkt_init()`, `usbhs_pkt_push()`, `usbhs_pkt_pop()`, `usbhs_pkt_start()`, `__usbhsf_pkt_get()`, `usbhs_fifo_probe/remove()`, `usbhs_fifo_init/quit()`, and `usbhs_fifo_clear_dcp()`. Exported packet handlers include PIO push/pop, DMA push/pop, DCP status/data stage handlers, and control-stage-end handler.

Core helpers are `usbhsf_pkt_handler()` for locked dispatch, `usbhsf_fifo_select/unselect/clear/barrier()`, IRQ control wrappers for `irq_bempsts`/`irq_brdysts`, PIO movers `usbhsf_pio_try_push()` and `usbhsf_pio_try_pop()`, DMA preparation/done paths, and `usbhsf_irq_empty/ready()` for interrupt-driven progress.

## Control Flow
Callers queue a packet with a pipe handler and start it. The handler prepares the transfer immediately or arms an interrupt/DMA. BRDY/BEMP IRQs iterate pipes with matching status bits and call TRY_RUN. DMA completion calls DMA_DONE, which may finish the packet or fall back to PIO for residual/zero-packet handling. When a packet finishes, it is removed from the pipe list, its `done` callback runs outside the lock, and the next queued packet starts.

## State And Persistence
State is stored in pipe packet lists, packet fields (`buf`, `length`, `actual`, `zero`, `sequence`, `dma`, `trans`, `dma_result`), pipe running/FIFO pointers, FIFO backpointers, DMA channels, and current mode IRQ masks. Hardware state includes FIFO selectors, counters, DREQE, BVAL/BCLR/FRDY/DTLN, BRDYSTS/BEMPSTS, and pipe PID/sequence.

## Dependencies And Integration Points
It depends on `pipe.c` for pipe access, mode modules for IRQ callback fields, DMAEngine for DFIFO channels, gadget/host DMA-map callbacks, and Renesas platform parameters such as `pio_dma_border`, `has_usb_dmac`, `cfifo_byte_addr`, and per-DFIFO slave IDs.

## Risks
FIFO ownership is represented by mutual `pipe->fifo` and `fifo->pipe` pointers; stale ownership causes `-EBUSY` or data corruption. DMA/PIO fallback depends on alignment, length, endpoint type, and hardware capability. Some DMA prep for non-USB-DMAC is punted to workqueue because DMA engine cannot be used in atomic context. Interrupt masks must be updated before/after FIFO state transitions. Error paths often convert temporary hardware busy into retry-by-interrupt.

## Test Signals
Test PIO IN/OUT, DMA IN/OUT, short packets, zero packets, DCP data/status stages, queue cancellation, DMA alignment fallbacks, BRDY/BEMP interrupt progress, DMA completion with residue, and repeated FIFO select/unselect under concurrent endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/fifo.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/fifo.h

## Purpose
`fifo.h` defines the FIFO and packet abstractions shared between the Renesas USBHS FIFO engine and host/gadget frontends.

## Important APIs, Types, And Functions
`struct usbhs_fifo` names one FIFO and stores port/selector/control register offsets, the currently selected pipe, TX/RX DMA channels, and legacy SH-DMA slave descriptors. `struct usbhs_fifo_info` embeds CFIFO and four DFIFOs. `struct usbhs_pkt` is the transfer unit: list node, pipe, handler, completion callback, DMA/work fields, buffer, lengths, zero-packet flag, and desired DATA sequence. `struct usbhs_pkt_handle` is a strategy table with `prepare`, `try_run`, and `dma_done` callbacks.

The header declares FIFO lifecycle functions, DCP clear, all standard packet handlers, and packet queue/start helpers.

## Control Flow
Host/gadget code sets `pipe->handler` to one of the declared handlers, fills a `usbhs_pkt` via `usbhs_pkt_push()`, then starts progress with `usbhs_pkt_start()`. FIFO code owns transitions between handler callbacks.

## State And Persistence
FIFO selection state is stored both in software (`fifo->pipe`, `pipe->fifo`) and hardware selector registers. Packet state persists until completion or dequeue.

## Dependencies And Integration Points
It includes interrupt, DMA, workqueue, `asm/dma.h`, and `pipe.h`. Gadget and host modules embed `usbhs_pkt` in their request wrappers and rely on these handler declarations.

## Risks
The `dma_result` pointer references DMAEngine callback data and must only be interpreted during completion handling. `usbhs_pkt` list ownership is subtle; freeing requests while `pkt.node` is linked is unsafe. Direction semantics are inherited from `pipe.c` and differ between host/gadget.

## Test Signals
Compile-time coverage plus runtime tests for packet lifetime, handler switching, DMA result accounting, and FIFO backpointer cleanup after dequeue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/fifo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod.c

## Purpose
`mod.c` implements mode registration/selection and the top-level interrupt dispatcher for Renesas USBHS. It arbitrates between host and gadget modules and handles autonomy-mode VBUS detection.

## Important APIs, Types, And Functions
Mode APIs include `usbhs_mod_register()`, `usbhs_mod_get()`, `usbhs_mod_get_current()`, `usbhs_mod_is_host()`, `usbhs_mod_change()`, `usbhs_mod_probe()`, and `usbhs_mod_remove()`. Autonomy helpers are `usbhs_mod_autonomy_mode()` and `usbhs_mod_non_autonomy_mode()`. Interrupt-facing helpers include `usbhs_status_get_device_state()`, `usbhs_status_get_ctrl_stage()`, `usbhs_interrupt()`, and `usbhs_irq_callback_update()`.

## Control Flow
Probe calls host and gadget probe helpers, then requests the shared controller IRQ. `usbhs_mod_change()` selects the current module, which later receives start/stop and IRQ callbacks. On interrupt, the dispatcher snapshots INTSTS0/1 and BRDYSTS/NRDYSTS/BEMPSTS under lock, clears hardware status registers using required magic masks, then calls VBUS, device-state, control-stage, buffer-empty/ready, attach/detach, setup ACK, and setup error callbacks according to current mode.

## State And Persistence
`struct usbhs_mod_info` holds registered modules, current module, VBUS IRQ callback, and VBUS getter. Each `struct usbhs_mod` stores function pointers and current BRDY/BEMP pipe masks. Hardware interrupt enable state is programmed by `usbhs_irq_callback_update()`.

## Dependencies And Integration Points
It bridges `common.c` hotplug state, `fifo.c` IRQ mask updates, and host/gadget callbacks. It uses `mod.h` conditional frontend probes so missing HCD/UDC support compiles to stubs.

## Risks
`usbhs_mod_change(-1)` sets current module to NULL but returns `-EINVAL`; callers intentionally ignore that in disconnect paths. `usbhs_mod_is_host()` returns `-EINVAL` when no mode is current, but several paths use it in boolean contexts, so no-current behaves as true-ish only if not checked carefully. Interrupt clear ordering is hardware-sensitive and must not be changed casually.

## Test Signals
Test IRQ dispatch in host and gadget mode, no-current/autonomy VBUS IRQs, BRDY/BEMP mask updates, attach/detach transitions, setup ACK/error completion, and hotplug mode changes while interrupts are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod.h

## Purpose
`mod.h` defines the internal mode abstraction and interrupt callback contract for Renesas USBHS host/gadget switching.

## Important APIs, Types, And Functions
`struct usbhs_irq_state` snapshots INTSTS0/1 and pipe status registers. `struct usbhs_mod` names a mode and stores start/stop hooks plus callback slots for DVST, CTRT, BEMP, BRDY, ATTCH, DTCH, SIGN, and SACK events. `struct usbhs_mod_info` stores registered host/gadget modules, the current module, autonomy VBUS callback, and VBUS getter.

The `usbhs_mod_call()` and `usbhs_mod_info_call()` macros safely invoke optional callbacks. Conditional prototypes/stubs for host/gadget probe/remove are controlled by `CONFIG_USB_RENESAS_USBHS_HCD` and `CONFIG_USB_RENESAS_USBHS_UDC`.

## Control Flow
The common hotplug path switches the current module and calls mode start/stop. The IRQ dispatcher uses the callback table to fan out hardware events. FIFO code mutates `irq_bempsts` and `irq_brdysts`, then calls `usbhs_irq_callback_update()`.

## State And Persistence
Persistent mode state is the registered callback tables and current mode pointer. The IRQ-state struct is transient per interrupt.

## Dependencies And Integration Points
It includes `common.h` and `linux/usb/renesas_usbhs.h` for mode IDs. It is consumed by every Renesas USBHS C file except small SoC headers.

## Risks
The call macros return 0 for missing callbacks, so missing functionality can fail silently. Header conditional stubs must stay aligned with Makefile object inclusion. Current-mode access assumes `usbhs_mod_register()` has populated the relevant slot before use.

## Test Signals
Build tests for frontend enabled/disabled cases, and runtime checks that mode callbacks are installed/removed during start/stop and that interrupt masks reflect callback availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod_gadget.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod_gadget.c

## Purpose
`mod_gadget.c` implements the USB gadget/UDC frontend for Renesas USBHS. It exposes endpoints to the composite gadget framework, translates `usb_request` objects into `usbhs_pkt` transfers, handles standard control requests that the controller can complete internally, manages pullup/VBUS state, and registers as the gadget mode module.

## Important APIs, Types, And Functions
`struct usbhsg_gpriv` embeds `usb_gadget`, `usbhs_mod`, current gadget driver, optional legacy transceiver, status flags, and endpoint array. `struct usbhsg_uep` wraps `usb_ep` and a pipe pointer. `struct usbhsg_request` wraps `usb_request` and `usbhs_pkt`.

Endpoint ops include enable/disable, alloc/free, queue/dequeue, set halt, and wedge. Gadget ops include `get_frame`, `set_selfpowered`, `udc_start`, `udc_stop`, `pullup`, and `vbus_session`. Mode hooks are `usbhsg_start()` and `usbhsg_stop()`.

## Control Flow
Probe allocates endpoint state, optionally gets a legacy PHY, registers the gadget mode, initializes endpoint capabilities from pipe configs, and calls `usb_add_gadget_udc()`. UDC start binds a gadget driver and optionally connects it to an OTG transceiver; start completes only when both cable/module and gadget-driver status bits are set. Starting initializes FIFO/pipe layers, allocates DCP, enables function mode, updates pullup, installs DVST/CTRT callbacks, and enables IRQs. Endpoint queues become `usbhs_pkt` objects using DMA-capable handlers. Control-stage IRQs choose DCP handlers, read setup packets, handle clear/set feature and get status locally, or call the gadget driver's `setup()`.

## State And Persistence
State includes gadget status flags (`STARTED`, `REGISTERD`, `WEDGE`, `SELF_POWERED`, `SOFT_CONNECT`), endpoint-to-pipe mappings, queued request packet nodes, `gadget.speed`, `vbus_active`, and optional PHY link. Hardware state includes function mode, D+ pullup, DCP/PIPE registers, FIFO state, and test mode.

## Dependencies And Integration Points
It depends on Linux USB gadget APIs, optional legacy USB PHY/OTG, internal FIFO/pipe/mod/common layers, and platform VBUS detection through `usbhsg_vbus_session()` or common hotplug.

## Risks
Locking crosses USB gadget callbacks: giveback deliberately drops the shared USBHS lock before calling completion. Endpoint disable must drain packets before freeing pipes. The direction helpers are easy to misread in gadget mode because pipe direction is from hardware perspective. Halt on IN endpoints returns `-EAGAIN` when queued/transmittable data exists. Standard request handling allocates atomic control-status buffers.

## Test Signals
Run enumeration with control transfers, descriptor fetches, set/clear halt, wedge behavior, zero-length packets, disconnect during queued I/O, pullup toggling, self-powered get-status, VBUS-session PHY mode, DMA and PIO fallback, and suspend state notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod_gadget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod_host.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod_host.c

## Purpose
`mod_host.c` implements the USB host controller frontend. It wraps the Renesas USBHS controller as a `usb_hcd`, emulates a one-port root hub, maps USB devices/endpoints onto a limited set of reusable hardware pipes, and translates URBs into `usbhs_pkt` transfers.

## Important APIs, Types, And Functions
`struct usbhsh_hpriv` embeds `usbhs_mod`, DCP pipe, fixed `usbhsh_device` slots, root-hub port status, and setup ACK completion. `struct usbhsh_device` maps a Linux `usb_device` to a controller DEVADD slot. `struct usbhsh_ep` maps a host endpoint to a pipe and holds a reuse counter. `struct usbhsh_request` wraps an URB and packet.

The `hc_driver` implements `urb_enqueue`, `urb_dequeue`, `endpoint_disable`, `hub_status_data`, `hub_control`, and no-op bus suspend/resume. Mode hooks are `usbhsh_start()` and `usbhsh_stop()`. Attach/detach/setup ACK/error IRQ callbacks update root-hub state and completions.

## Control Flow
Probe creates an HCD, registers the host mode, and initializes device slots. Starting adds the HCD, initializes FIFO/pipe layers, creates host pipes with direction assignment, enables host mode, and installs attach/detach/setup IRQ callbacks. URB enqueue links the URB, attaches a device slot if needed, attaches endpoint metadata, attaches a free compatible pipe, then either sends DCP setup/data/status stages or queues a normal packet. Queue completion updates URB length, saves DATA0/1 sequence for reused pipes, detaches the pipe, unlinks, and gives back the URB. Root-hub reset drives USB reset, waits for speed, and enables SOF.

## State And Persistence
State includes the HCD private area, device slot array, endpoint lists and pipe counters, root-hub port status bits, setup completion, URB `hcpriv`, endpoint `hcpriv`, and USB device drvdata mappings. Pipe DATA toggle persistence is maintained in the Linux USB core toggles because hardware pipes are reused across endpoints/devices.

## Dependencies And Integration Points
It depends on Linux USB HCD APIs, internal pipe/FIFO/common/mod layers, DMA mapping callbacks, root-hub request definitions, and Renesas DEVADDn hardware limits.

## Risks
The controller can address only a limited number of devices and pipes, so slot exhaustion and pipe reuse are central failure modes. Setup stage waits indefinitely for SACK/SIGN completion, so missing IRQs can hang. DCP SET_ADDRESS rewrites the requested USB address to the internal device slot number. Isochronous URBs are rejected. Error unwind after `usb_hcd_link_urb_to_ep()` does not visibly unlink in every failure branch in this source snapshot, which should be reviewed with the surrounding kernel version.

## Test Signals
Test device attach/detach, root-hub port reset/speed detection, SET_ADDRESS, hub-attached devices, slot exhaustion, endpoint disable while URBs are queued, bulk/interrupt IN/OUT, DATA toggle correctness across pipe reuse, URB dequeue, and missing setup ACK/error interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod_host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/pipe.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/pipe.c

## Purpose
`pipe.c` manages Renesas USBHS hardware pipes. It allocates pipes by transfer type/direction, configures PIPECFG/PIPEBUF/PIPEMAXP/DCP registers, controls PID/STALL/DATA sequence, clears buffers, sets bulk transfer counters, and connects pipes to FIFOs and host/gadget private endpoint state.

## Important APIs, Types, And Functions
Public APIs include `usbhs_pipe_probe/remove()`, `usbhs_pipe_init()`, `usbhs_pipe_malloc/free()`, `usbhs_dcp_malloc()`, `usbhs_pipe_config_update()`, `usbhs_pipe_enable/disable/stall/is_stall()`, `usbhs_pipe_clear()`, `usbhs_pipe_clear_without_sequence()`, `usbhs_pipe_config_change_bfre()`, `usbhs_pipe_set_trans_count_if_bulk()`, `usbhs_pipe_select_fifo()`, and direction/running predicates.

Important internal helpers are register accessors for DCP versus selected PIPE registers, `usbhsp_pipe_barrier()` for safe reconfiguration, `usbhsp_setup_pipecfg()`, and `usbhsp_setup_pipebuff()`.

## Control Flow
Probe allocates the pipe array from platform pipe configs and records each type. Mode start calls `usbhs_pipe_init()` to reset flags, lists, FIFO links, and hardware buffers. Endpoint enable/host start allocates compatible unused pipes, waits for barrier, writes config/buffer registers, clears buffers, and sets DATA0. Transfer paths enable/disable/stall pipes and adjust DATA sequence. Free clears PIPECFG and flags.

## State And Persistence
Each `usbhs_pipe` stores type, private controller pointer, FIFO pointer, queued packet list, maxpacket, flags (`IS_USED`, `IS_DIR_IN`, `IS_DIR_HOST`, `IS_RUNNING`), current handler, and mode-private endpoint pointer. Hardware state includes PIPESEL, PIPECFG, PIPEBUF, PIPEMAXP, PIPEnCTR/DCPCTR, transaction counters, and DATA toggle bits.

## Dependencies And Integration Points
It depends on platform pipe configs from `renesas_usbhs.h`, common register definitions, FIFO clearing for DCP, and host/gadget allocation patterns.

## Risks
Safe register update requires NAK, no busy, and no selected FIFO; violating `usbhsp_pipe_barrier()` semantics can corrupt transfers. Direction flags are set with host/gadget semantics and can be confusing. Transaction counters are only programmed for bulk IN. `usbhs_pipe_clear_without_sequence()` preserves DATA toggle around buffer clear and BFRE changes; losing that breaks protocol correctness.

## Test Signals
Test pipe allocation exhaustion, DCP and non-DCP configuration, host/gadget direction combinations, stall/unstall, DATA0/1 preservation across clears, bulk transfer counter setup, FIFO link cleanup, and barriers when hardware stays busy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/pipe.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/pipe.h

## Purpose
`pipe.h` declares the Renesas USBHS pipe abstraction and pipe-management API used by common, FIFO, host, and gadget code.

## Important APIs, Types, And Functions
`struct usbhs_pipe` stores the transfer type, owning `usbhs_priv`, selected FIFO, packet list, maxpacket, flags, current packet handler, and mode-private pointer. `struct usbhs_pipe_info` owns the pipe array and the mode-provided DMA map/unmap callback. Iteration macros cover pipes with or without DCP.

The header declares allocation/free, probe/remove, direction/running predicates, clear/enable/disable/stall helpers, transfer-counter and BFRE helpers, FIFO selection, config update, sequence control, and DCP helpers.

## Control Flow
Mode modules allocate DCP or regular pipes, update endpoint/device config, assign handlers, then FIFO code consumes pipe fields during transfer. Host/gadget teardown frees or clears pipes through these declarations.

## State And Persistence
Pipe state is in-memory plus mirrored hardware state in the registers managed by `pipe.c`. The list head owns queued `usbhs_pkt` objects until completion/cancellation.

## Dependencies And Integration Points
It includes `common.h` and `fifo.h`, creating a tight internal API cycle. It is not a public platform header; external parameters come from `linux/usb/renesas_usbhs.h`.

## Risks
`usbhs_pipe_type(p)` is a macro lvalue used during probe, which is convenient but easy to misuse. `usbhs_pipe_is_busy()` only means a FIFO is selected, not that the hardware is electrically busy. Direction helpers must be interpreted with mode context.

## Test Signals
Compile checks for all modules and runtime assertions around pipe list lifetime, FIFO selection, DCP identification, and mode-specific direction decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/pipe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar2.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar2.c

## Purpose
This file provides R-Car Gen2 platform callbacks and driver parameters for Renesas USBHS.

## Important APIs, Types, And Functions
`usbhs_rcar2_hardware_init()` obtains the generic PHY named `"usb"` when `CONFIG_GENERIC_PHY` is enabled and stores it in `priv->phy`. `usbhs_rcar2_hardware_exit()` puts that PHY. `usbhs_rcar2_power_ctrl()` calls `phy_init()`/`phy_power_on()` on enable and `phy_power_off()`/`phy_exit()` on disable. `usbhs_rcar_gen2_plat_info` exports these callbacks and sets `has_usb_dmac` and `has_new_pipe_configs`.

## Control Flow
`common.c` calls hardware init during probe, power control during runtime power transitions, and hardware exit during remove. ID selection is fixed to gadget by `usbhs_get_id_as_gadget()`.

## State And Persistence
Persistent state is the `priv->phy` pointer and the generic PHY's power/init state. The exported platform-info object is static const.

## Dependencies And Integration Points
It depends on Linux generic PHY APIs and the Renesas USBHS common platform-callback contract. OF match entries in `common.c` select this platform info for R-Car Gen2 compatibles.

## Risks
If `CONFIG_GENERIC_PHY` is not enabled, hardware init returns `-ENXIO`. A `phy_init()` success followed by `phy_power_on()` failure does not call `phy_exit()` in this function, so callers depend on later disable/unwind behavior. Gen2 is forced gadget by this callback set unless another platform data path overrides it.

## Test Signals
Test probe with and without generic PHY support, missing `"usb"` PHY, power on/off balance, PHY power-on failure, and DT compatibles mapped to Gen2 platform info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar2.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar2.h

## Purpose
This header declares the R-Car Gen2 USBHS platform-info export.

## Important APIs, Types, And Functions
It includes `common.h` and declares `extern const struct renesas_usbhs_platform_info usbhs_rcar_gen2_plat_info;`.

## Control Flow
There is no runtime flow. `common.c` references the symbol from its OF match table; `rcar2.c` defines it.

## State And Persistence
No state is stored here beyond the declaration contract.

## Dependencies And Integration Points
The header ties `common.c` match data to the Gen2 implementation file.

## Risks
Any rename or signature mismatch breaks the OF match table build. Including `common.h` pulls a broad internal dependency graph into this small declaration.

## Test Signals
Build with R-Car Gen2 compatibles enabled and verify `usbhs_rcar_gen2_plat_info` links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar3.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar3.c

## Purpose
This file provides R-Car Gen3 platform power callbacks and platform-info variants, including a PLL-control path for SoCs that need UGCTRL PLL reset handling.

## Important APIs, Types, And Functions
It defines 32-bit helpers `usbhs_write32()`/`usbhs_read32()`, `usbhs_rcar3_set_ugctrl2()` to preserve reserved UGCTRL2 bits, `usbhs_rcar3_power_ctrl()` for standard Gen3 low-power/SUSPM control, and `usbhs_rcar3_power_and_pll_ctrl()` for D3-like PLL reset/lock/connect sequencing. It exports `usbhs_rcar_gen3_plat_info` and `usbhs_rcar_gen3_with_pll_plat_info`, both enabling USB-DMAC, multi-clock mode, and new pipe configs.

## Control Flow
On power enable, standard Gen3 selects OTG/VBUS in UGCTRL2, sets LPSTS.SUSPM, and waits 45-90 us. The PLL variant releases PLL reset, sets UGCTRL2, enables SUSPM, polls UGSTS.LOCK up to about 1 ms, then writes UGCTRL.CONNECT. Disable reverses SUSPM and asserts PLL reset in the PLL variant.

## State And Persistence
State is hardware register state in LPSTS, UGCTRL, UGCTRL2, and UGSTS. Platform-info objects are static const.

## Dependencies And Integration Points
Selected by Gen3 and compatible-specific OF entries in `common.c`. It uses common 16-bit register helpers for LPSTS and local 32-bit helpers for UGCTRL registers.

## Risks
The PLL-lock loop ignores timeout as a return error; failure to lock still proceeds to CONNECT. UGCTRL2 reserved bit handling is mandatory. Multi-clock driver parameter requires matching DT clocks. These callbacks force gadget ID via `usbhs_get_id_as_gadget()`.

## Test Signals
Test standard and with-PLL compatibles, clock arrays, power enable/disable register sequences, UGSTS lock timeout behavior, and suspend/resume power cycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar3.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar3.h

## Purpose
This header declares the R-Car Gen3 USBHS platform-info exports.

## Important APIs, Types, And Functions
It declares `usbhs_rcar_gen3_plat_info` and `usbhs_rcar_gen3_with_pll_plat_info`.

## Control Flow
No executable flow exists. The OF match table in `common.c` references these symbols; `rcar3.c` defines them.

## State And Persistence
The header stores no state.

## Dependencies And Integration Points
It includes `common.h` for `struct renesas_usbhs_platform_info` and connects common match data to Gen3 platform glue.

## Risks
Declaration mismatch breaks links for Gen3 compatibles. Adding a new Gen3 variant requires updating both this header and the match table.

## Test Signals
Build all Gen3 compatible paths and verify both platform-info symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza.c

## Purpose
This file provides RZ/A1 USBHS hardware initialization and platform information.

## Important APIs, Types, And Functions
`usbhs_rza1_hardware_init()` discovers `usb_x1` and `extal` clock nodes, reads their `clock-frequency`, selects 12 MHz XTAL through SYSCFG.UCKSEL when no 48 MHz USB clock is present and EXTAL is 12 MHz, enables the USB PLL with SYSCFG.UPLLE, waits 1-2 ms, and sets SUSPMODE.SUSPM. `usbhs_rza1_plat_info` exports this init callback, gadget ID selection, and `has_new_pipe_configs`.

## Control Flow
`common.c` invokes hardware init during probe after resets and before hotplug. If neither a 48 MHz USB clock nor 12 MHz EXTAL is detected, init returns `-EIO`.

## State And Persistence
State is hardware clock-source/PLL/SUSPMODE programming. The platform-info object is static const.

## Dependencies And Integration Points
It depends on OF global node lookup by names `"usb_x1"` and `"extal"`, common register helpers, and RZ/A-compatible match entries in `common.c`. `rza.h` also declares platform info for RZ/A2 and RZ/G2L defined in `rza2.c`.

## Risks
Global node-name lookup is fragile and not scoped to the USB device. Missing clock nodes default frequency variables to zero, potentially forcing the EXTAL validation path. Only RZ/A1 is defined here; related symbols are declared elsewhere. The callback forces gadget ID.

## Test Signals
Test DTs with 48 MHz USB clock, 12 MHz EXTAL fallback, invalid/missing clocks, PLL/SUSPMODE register effects, and probe failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza.h

## Purpose
This header declares RZ-family USBHS platform-info exports.

## Important APIs, Types, And Functions
It declares `usbhs_rza1_plat_info`, `usbhs_rza2_plat_info`, and `usbhs_rzg2l_plat_info`.

## Control Flow
No runtime flow is in the header. `common.c` selects these symbols via compatible match data; `rza.c` defines the RZ/A1 symbol and `rza2.c` defines the RZ/A2 and RZ/G2L symbols.

## State And Persistence
No state is stored here.

## Dependencies And Integration Points
It includes `common.h` and acts as the bridge between common match data and RZ-family glue implementations.

## Risks
The header declares symbols not defined in `rza.c`; readers must include the Makefile-linked `rza2.o` to resolve them. Renaming or removing declarations breaks the OF match table build.

## Test Signals
Build all RZ/A1, RZ/A2, and RZ/G2L match paths and verify symbol linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rza.h -->
