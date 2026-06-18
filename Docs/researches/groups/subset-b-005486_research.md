# Research: subset-b-005486

Grouped DWC3 research for `subset-b-005486`. Each file section is bounded by the reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/core.c

## Purpose
`core.c` is the central Synopsys DesignWare USB3 DWC3 controller driver. It validates the hardware ID and hardware parameters, maps the DWC3 global/device register window, discovers clocks, resets, PHYs, extcon/role-switch state, and power-supply integration, then initializes the controller in host, gadget, or dual-role mode. It also exports core lifecycle and PM helpers for platform glue drivers that embed `struct dwc3` directly.

## Important APIs, Types, and Functions
The exported core API includes `dwc3_core_probe()`, `dwc3_core_remove()`, `dwc3_core_init()`, `dwc3_core_exit()`, `dwc3_core_soft_reset()`, `dwc3_set_prtcap()`, `dwc3_set_mode()`, `dwc3_enable_susphy()`, event-buffer setup/cleanup, runtime PM helpers, and system PM helpers. `dwc3_probe()` is the standalone platform wrapper for compatible strings such as `snps,dwc3`.

Important internal setup functions are `dwc3_get_properties()`, `dwc3_get_software_properties()`, `dwc3_get_dr_mode()`, `dwc3_core_is_valid()`, `dwc3_cache_hwparams()`, `dwc3_core_get_phy()`, `dwc3_phy_setup()`, `dwc3_phy_init()`, `dwc3_phy_power_on()`, `dwc3_get_num_ports()`, and `dwc3_core_init_mode()`. Register programming is concentrated in helpers for GCTL/GUCTL/GFLADJ, GSBUSCFG0, threshold registers, USB2/USB3 PHY config, and DWC31/DWC32 revision-specific workarounds.

## Control Flow
Probe takes the memory resource, reserves the DWC3 global range while leaving xHCI registers for the child xHCI driver, maps registers, reads properties, grabs power supply, resets/clocks, validates IP ID, caches HWPARAMS, sets DMA masks, determines port counts, enables runtime PM, allocates event buffers, resolves extcon, coerces `dr_mode` to match hardware and build-time host/gadget support, initializes the core, starts debugfs, then initializes the selected role. Error paths unwind in reverse order: role/debugfs/event buffers, PHYs, ULPI, runtime PM, clocks, reset, and power supply.

Dual-role changes are asynchronous through `dwc3_set_mode()` and `__dwc3_set_mode()` on `system_freezable_wq`. The worker exits the current host/gadget/OTG role, may issue a GCTL core soft reset for DRD switching, sets `GCTL.PrtCapDir`, and initializes the target role, including VBUS and generic PHY mode changes. Gadget transitions set event buffers before gadget init; host transitions set VBUS and all PHY ports to host mode.

## State and Persistence Behavior
All persistent runtime state lives in `struct dwc3`: cached hardware params, IP/revision/version type, current/desired role, OTG role state, event buffer pointer, PHY pointers, clocks, reset, debugfs regset, power-supply pointer, quirk bits, runtime PM flags, and suspend bookkeeping. No disk persistence exists. Hardware register state is reprogrammed on probe, role switch, resume, and full reinit paths. Event buffers are coherent DMA allocations with a software cache and are masked/cleared on cleanup.

## Dependencies and Integration Points
The file integrates Linux platform driver, OF/ACPI properties, runtime PM, pinctrl PM, clk/reset frameworks, USB PHY and generic PHY frameworks, extcon, usb-role-switch, xHCI child resources, power_supply current limit programming, debugfs, and the DWC3 gadget/host/OTG modules. Platform glue drivers can call `dwc3_core_probe()` with `ignore_clocks_and_resets`, `skip_core_init_mode`, or software `dwc3_properties`.

## Risks
Main risks are ordering-sensitive register and PHY sequencing, revision-specific workarounds, DRD races between workqueue mode changes and PM, array bounds for multiport PHYs, event-buffer cleanup when device halt fails, and property combinations that force unsupported speeds or modes. PM paths are especially sensitive: host runtime suspend may leave PHY PM to xHCI, gadget suspend tears down the core when active, and system suspend may force SUSPHY for wake-capable platforms.

## Test Signals
Useful signals are successful probe/remove in host, peripheral, and OTG configurations; xHCI child enumeration; gadget enumeration and disconnect; role switch via extcon, USB role switch, and debugfs; runtime autosuspend/resume while disconnected; system suspend/resume with wake enabled and disabled; soft-reset timeout logging; debugfs `regdump`, `mode`, and `link_state`; DMA mask setup on 64-bit DWC3; multiport host enumeration; and regression tests for all quirk properties parsed in `dwc3_get_properties()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/core.h -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/core.h

## Purpose
`core.h` is the shared hardware and software contract for the DWC3 driver family. It defines register offsets, bit fields, hardware revision constants, event formats, transfer descriptors, endpoint/request/controller state structures, feature flags, and function prototypes used by core, gadget, host, OTG, debugfs, and glue drivers.

## Important APIs, Types, and Functions
Key data types are `struct dwc3`, `struct dwc3_ep`, `struct dwc3_request`, `struct dwc3_trb`, `struct dwc3_event_buffer`, `struct dwc3_hwparams`, `struct dwc3_glue_ops`, `union dwc3_event`, `struct dwc3_event_depevt`, and `struct dwc3_event_devt`. The header also defines endpoint flags, request status constants, EP0 states, USB link states, DWC3/DWC31/DWC32 revision identifiers, and register helpers such as `DWC3_GUSB2PHYCFG(n)`, `DWC3_GUSB3PIPECTL(n)`, `DWC3_DEPCMD(n)`, and TRB field macros.

The public prototypes cover role switching, FIFO-space reads, event-buffer setup, core soft reset, SUSPHY control, host/gadget/DRD/OTG/ULPI entry points, and PM suspend/resume hooks. Static inline fallbacks make host, gadget, DRD, and ULPI calls compile away when the related Kconfig support is disabled.

## Control Flow
The header does not execute control flow directly, but it shapes every driver path. `struct dwc3` is the hub of probe, mode switching, interrupt/event processing, PM, and debugfs. `work_to_dwc()` connects the DRD work item back to the controller. Version macros such as `DWC3_VER_IS_WITHIN()` gate workarounds in `core.c` and gadget paths. Event structures define how raw 32-bit event-buffer entries are decoded into endpoint, device, and global events.

## State and Persistence Behavior
The header defines volatile in-memory state only. `struct dwc3` stores hardware-derived fields, role state, endpoint arrays, DMA buffers, PHY/clock/reset handles, quirk flags, PM flags, debugfs handles, and gadget transfer state. Endpoint state tracks TRB enqueue/dequeue positions, request lists, resource indexes, stream flags, and workaround fields. None of this is persistent across driver unload or full hardware power loss; `core.c` and glue drivers rebuild it during probe or resume.

## Dependencies and Integration Points
The contract depends on Linux USB gadget, OTG, role-switch, ULPI, PHY, DMA, debugfs, wait/completion, workqueue, power-supply, mutex, and spinlock types. Integration points include `dwc3_glue_ops` callbacks for platform-specific role/run-stop notifications, Kconfig-gated host/gadget/dual-role functions, and hardware register definitions consumed by core, gadget, ep0, host, OTG, debugfs, and platform glue sources.

## Risks
This file is high blast-radius because field layout, bit definitions, and helper macros are used across the entire DWC3 subsystem. Risks include incorrect packed event bitfields, mismatched revision constants, unsafe assumptions about `DWC3_TRB_NUM` fitting in `u8` enqueue/dequeue indexes, multiport array limits, fallback stubs hiding missing Kconfig functionality, and broad `struct dwc3` state coupling across locking domains.

## Test Signals
Build coverage across host-only, gadget-only, dual-role, debugfs, and ULPI Kconfig combinations is essential. Runtime signals include correct event decoding, endpoint ring traversal, role switch state, PM callbacks, multiport bounds, and version-specific workarounds. Static analysis should pay attention to bitfield packing, DMA structure sizes, and uses of version macros that assume a local `dwc` variable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/debug.h -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/debug.h

## Purpose
`debug.h` provides inline formatting helpers for DWC3 modes, commands, link states, endpoint/device events, TRB types, EP0 state, and command status values. It also declares debugfs lifecycle hooks when `CONFIG_DEBUG_FS` is enabled and provides no-op stubs otherwise.

## Important APIs, Types, and Functions
Important helpers include `dwc3_mode_string()`, `dwc3_gadget_ep_cmd_string()`, `dwc3_gadget_generic_cmd_string()`, `dwc3_gadget_link_string()`, `dwc3_gadget_hs_link_string()`, `dwc3_trb_type_string()`, `dwc3_ep0_state_string()`, `dwc3_gadget_event_string()`, `dwc3_ep_event_string()`, `dwc3_gadget_event_type_string()`, `dwc3_decode_event()`, `dwc3_ep_cmd_status_string()`, and `dwc3_gadget_generic_cmd_status_string()`. Debugfs APIs are `dwc3_debugfs_create_endpoint_dir()`, `dwc3_debugfs_remove_endpoint_dir()`, `dwc3_debugfs_init()`, and `dwc3_debugfs_exit()`.

## Control Flow
Most helpers are switch statements mapping register or event constants from `core.h` to stable human-readable strings. `dwc3_decode_event()` copies a raw 32-bit event into `union dwc3_event`, then dispatches to device-event or endpoint-event decoding based on `evt.type.is_devspec`. Endpoint event formatting includes EP number/direction, transfer status bits, control endpoint phase, stream status, and EP0 state where relevant.

## State and Persistence Behavior
The file has no persistent state. It formats caller-provided event/status values into caller-provided buffers. The debugfs declarations are compile-time integration points and become no-ops without debugfs support.

## Dependencies and Integration Points
It depends directly on `core.h` constants and event structures. It is consumed by trace/debug logging, `debugfs.c`, gadget command/event paths, and core role/debug paths. The header deliberately centralizes string conversion so diagnostic output stays consistent across tracepoints and debugfs.

## Risks
String helpers can drift from hardware constants, especially when new DWC3/DWC31/DWC32 event or TRB types are added. `dwc3_decode_event()` assumes the raw event layout in `union dwc3_event` matches hardware and compiler packing. Formatting truncation is bounded by `snprintf()`/`scnprintf()`, but callers must provide adequate buffers for diagnostic clarity.

## Test Signals
Useful checks include trace/debugfs output for device events, endpoint transfer events, stream events, EP0 phases, command status returns, TRB ring dumps, and link-state displays at high speed and SuperSpeed. Kconfig builds with and without debugfs should confirm the debugfs hooks compile to working functions or no-op stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/debugfs.c

## Purpose
`debugfs.c` exposes DWC3 diagnostic and control surfaces under the USB debugfs root. It provides a broad register dump, LSP mux access, current mode reporting and role switching, gadget test-mode control, link-state display/control, and per-endpoint FIFO/queue/TRB/debug-register views.

## Important APIs, Types, and Functions
The file defines `dwc3_regs[]`, a `debugfs_reg32` table spanning global, PHY, FIFO, event, device, endpoint, and OTG registers. Public functions are `dwc3_debugfs_init()`, `dwc3_debugfs_exit()`, `dwc3_debugfs_create_endpoint_dir()`, and `dwc3_debugfs_remove_endpoint_dir()`. File operations cover `lsp_dump`, `mode`, `testmode`, `link_state`, and endpoint attributes such as `tx_fifo_size`, `rx_fifo_size`, request queues, `transfer_type`, `trb_ring`, and `GDBGEPINFO`.

## Control Flow
Initialization allocates `dwc->regset`, initializes `dbg_lsp_select`, creates a per-device directory, installs `regdump`, `lsp_dump`, optional dual-role `mode`, and optional gadget `testmode`/`link_state` files. Endpoint directories are created later by gadget endpoint setup and contain the endpoint map files. Most read paths call `pm_runtime_resume_and_get()`, take `dwc->lock`, read relevant DWC3 registers, format with `seq_file`, unlock, and drop runtime PM. Write paths parse small user buffers, then update `dbg_lsp_select`, call `dwc3_set_mode()`, call `dwc3_gadget_set_test_mode()`, or request a gadget link-state transition.

## State and Persistence Behavior
The only additional controller state is `dwc->regset`, `dwc->debug_root`, and `dwc->dbg_lsp_select`. Debugfs writes change live hardware/controller state but are not persistent across unload, reset, or reboot. Endpoint debug views read live rings and FIFO state; they do not snapshot or store history.

## Dependencies and Integration Points
The file integrates debugfs, seq_file, runtime PM, the DWC3 register accessors, `core.h` register definitions, `debug.h` string helpers, and gadget helpers for test mode/link-state control. It is initialized from `dwc3_core_probe()` after the core is initialized and removed before core exit.

## Risks
Debugfs is privileged but still dangerous: role switching, test mode, and link-state writes can disrupt active traffic. Register dump coverage includes fixed slots for ports/FIFOs/endpoints and must remain aligned with multiport limits. Runtime PM failure handling is basic, and live TRB-ring reads depend on the endpoint lock preventing concurrent mutation. The endpoint debug directory remove path uses lookup-and-remove by name, so endpoint naming consistency matters.

## Test Signals
Mount debugfs and verify `regdump`, `lsp_dump`, `mode`, `testmode`, and `link_state` appear according to Kconfig/mode. Exercise reads during runtime suspend and active transfer. In gadget mode, check link-state and test-mode writes. In dual-role mode, write `host`, `device`, and `otg` to `mode`. For endpoints, confirm FIFO and TRB files are created/removed with endpoint enable/disable and do not crash on EP0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/drd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/drd.c

## Purpose
`drd.c` implements DWC3 dual-role support. It connects role decisions from usb-role-switch, extcon, or the DWC3 OTG block to the core role-switch worker in `core.c`, and it programs OTG registers for simple host/device operation without full SRP/HNP support.

## Important APIs, Types, and Functions
Exported/internal integration functions are `dwc3_drd_init()`, `dwc3_drd_exit()`, `dwc3_otg_init()`, `dwc3_otg_exit()`, `dwc3_otg_update()`, and `dwc3_otg_host_init()`. Key helpers are `dwc3_otg_enable_events()`, `dwc3_otg_disable_events()`, `dwc3_otg_clear_events()`, `dwc3_otgregs_init()`, `dwc3_otg_get_irq()`, `dwc3_otg_host_exit()`, `dwc3_otg_device_init()`, `dwc3_otg_device_exit()`, `dwc3_drd_update()`, extcon notifier `dwc3_drd_notifier()`, and role-switch callbacks when `CONFIG_USB_ROLE_SWITCH` is enabled.

## Control Flow
`dwc3_drd_init()` prefers a USB role switch when the `usb-role-switch` property is present. Otherwise, it registers an extcon notifier if an extcon exists; extcon host state maps to host/device `GCTL.PrtCapDir` requests. Without role switch or extcon, it uses the DWC3 OTG block: obtains an OTG IRQ, clears/disables events, requests a threaded IRQ, initializes OTG registers, and schedules OTG role handling through `dwc3_set_mode(DWC3_GCTL_PRTCAP_OTG)`.

OTG IRQ top half reads and clears OEVT, filters non-OTG events, and wakes the thread. The thread handles pending host restart and requeues OTG mode evaluation. `dwc3_otg_update()` reads ID status unless told to ignore it, exits the current OTG sub-role, sets `current_otg_role`, initializes host or device OTG register flow, invokes glue `pre_set_role`, and starts `dwc3_host_init()` or `dwc3_gadget_init()`.

## State and Persistence Behavior
DRD state is stored in `struct dwc3`: `current_dr_role`, `desired_dr_role`, `current_otg_role`, `desired_otg_role`, `otg_restart_host`, `edev`, `edev_nb`, `role_sw`, `role_switch_default_mode`, and `otg_irq`. No persistence exists beyond the live driver instance. IRQ and notifier registrations are unwound by `dwc3_drd_exit()`.

## Dependencies and Integration Points
This file integrates extcon, usb-role-switch, OF platform population for connector devices, DWC3 OTG registers, gadget/host init and exit, event-buffer setup/cleanup for device role, and optional glue callbacks. It relies on the role-switch workqueue logic in `core.c` for non-OTG mode changes.

## Risks
Role switching is concurrency-sensitive: extcon/role-switch callbacks, debugfs mode writes, OTG IRQ thread, and PM can all touch role state. OTG register programming intentionally avoids SRP/HNP, so it is suitable for simple dual-role but not full OTG negotiation. Cleanup must match the current live role because users may change role through debugfs. A failed `dwc3_host_init()` or `dwc3_gadget_init()` leaves role registers updated but functionality unavailable.

## Test Signals
Test usb-role-switch set/get, extcon host cable notification, raw OTG ID changes, debugfs mode changes, unload while in each role, and suspend/resume around role changes. Hardware signals include VBUS assertion in host, gadget enumeration in device, OTG IRQ delivery, and no duplicate notifier/IRQ registration after reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/drd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-am62.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-am62.c

## Purpose
`dwc3-am62.c` is the TI AM62 USB wrapper glue driver. It configures TI-specific USBSS registers, PHY PLL reference clock selection through syscon, an i2409 PHY workaround, VBUS divider selection, mode-valid signaling, wakeup configuration, and parent PM before populating the child DWC3 core.

## Important APIs, Types, and Functions
The private type is `struct dwc3_am62`, storing wrapper MMIO, USB2 reference clock, syscon offset/rate code, optional PHY MMIO, VBUS divider flag, and last wakeup status. Key functions are `phy_syscon_pll_refclk()`, `dwc3_ti_init()`, `dwc3_ti_probe()`, `dwc3_ti_remove()`, `dwc3_ti_suspend_common()`, and `dwc3_ti_resume_common()`. The driver matches `ti,am62-usb`.

## Control Flow
Probe maps USBSS registers, gets the `ref` clock, converts its rate to a TI rate-code table entry, optionally maps PHY registers for the i2409 LDO reference workaround, reads `ti,vbus-divider`, and calls `dwc3_ti_init()`. Initialization programs syscon core voltage/refclk fields, applies the PLL LDO workaround when possible, sets VBUS divider selection, enables the ref clock, and sets `USBSS_MODE_VALID`. Probe then enables runtime PM, populates child devices, marks the wrapper wake-capable, enables wakeup, and starts autosuspend.

Suspend configures wake sources based on current operational mode in `USBSS_CORE_STAT`: host uses linestate/overcurrent wake, device uses VBUS/session-valid wake. It clears wake status, writes a debug sentinel to detect context loss, and disables the ref clock. Resume checks the sentinel; if context was lost it reruns full TI init, otherwise it restores debug config and reenables the ref clock, disables wake config, and records wakeup status.

## State and Persistence Behavior
Driver state is live only in `struct dwc3_am62`. Hardware wrapper state may be lost across suspend; the debug config sentinel determines whether to reinitialize. `wakeup_stat` retains the last wake reason after resume for possible diagnostics but is not exported here.

## Dependencies and Integration Points
The driver depends on platform MMIO resources, clk, syscon/regmap, OF child population, runtime PM, pinctrl consumer headers, and the DWC3 child core. It does not embed `struct dwc3`; it creates child devices via `of_platform_populate()`.

## Risks
Unsupported ref clock rates fail probe. If optional PHY MMIO mapping fails, the i2409 workaround is skipped with a warning, which may affect affected silicon. Wake configuration is mode-dependent and can cause missed or spurious wakeups if wrapper operational mode is stale. Remove clears mode-valid but does not explicitly disable the ref clock outside PM state transitions.

## Test Signals
Check probe with every supported reference clock rate, `ti,syscon-phy-pll-refclk` programming, optional PHY-resource absence, child DWC3 creation, runtime autosuspend, host/device wake from system suspend, context-loss reinitialization path, mode-valid bit clear on remove, and wakeup status capture after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-am62.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-apple.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-apple.c

## Purpose
`dwc3-apple.c` is the Apple Silicon DWC3 glue driver. It handles a platform where DWC3, USB2/USB3 PHY mode selection, Type-C cable orientation, resets, and Apple-specific CIO registers must be sequenced very carefully. Unlike normal glue, the core probe may be deferred until the first cable role event.

## Important APIs, Types, and Functions
The state model is `enum dwc3_apple_state`: `PROBE_PENDING`, `NO_CABLE`, `HOST`, and `DEVICE`. `struct dwc3_apple` embeds `struct dwc3`, stores Apple MMIO, reset, USB role switch, lock, and resource pointers. Key functions are `dwc3_apple_core_probe()`, `dwc3_apple_core_init()`, `dwc3_apple_init()`, `dwc3_apple_exit()`, role-switch set/get callbacks, `dwc3_apple_setup_role_switch()`, `dwc3_apple_probe()`, and `dwc3_apple_remove()`.

## Control Flow
Probe asserts reset, obtains the DWC3 core resource and Apple-specific MMIO, sets state to `PROBE_PENDING`, and registers a USB role switch. It deliberately does not call `dwc3_core_probe()` yet because the PHY needs cable mode/orientation first. On role switch to host or device, the mutex-protected set callback exits any current role, configures the USB2 PHY mode while powered off, deasserts reset, probes or reinitializes the core, programs Apple CIO timing/LFPS registers, sets DWC3 `dr_mode` and PRTCAP, enables SUSPHY, sets USB3 PHY mode, and starts xHCI or gadget. On `USB_ROLE_NONE`, it tears down host/gadget, keeps SUSPHY enabled for PHY shutdown sequencing, exits the core, asserts reset, and returns to `NO_CABLE`.

## State and Persistence Behavior
State is the explicit enum plus the embedded `struct dwc3`. The driver intentionally destroys and recreates live hardware state on every cable disconnect or role change. No persistent storage exists. `dwc3_core_probe()` is called once after first cable connect; later cable cycles use `dwc3_core_init()`.

## Dependencies and Integration Points
The driver uses reset controls, USB role switch, generic PHY modes, Apple-specific MMIO registers, and the exported DWC3 core/host/gadget APIs. It passes `ignore_clocks_and_resets` and `skip_core_init_mode` to `dwc3_core_probe()` because this glue owns the reset and role startup sequence.

## Risks
Ordering is the dominant risk. Comments document possible nonfunctional ports, watchdog resets, or SoC-level reset if PHY/core sequencing is wrong. State transitions must be serialized by the mutex. Remove currently obtains driver data via the embedded core pointer, which only exists after core probe has set drvdata; if no cable ever connected, that path must remain valid in the surrounding driver model. Unknown Apple CIO register values are empirical and hardware-specific.

## Test Signals
Test no-cable boot, first host connect, first device connect, repeated connect/disconnect, host-to-device flips, duplicate role notifications, remove before first cable event, remove after active role, USB2-only and USB3 devices, Type-C orientation changes, and absence of watchdog resets. Verify DWC3 debug output, xHCI/gadget enumeration, and reset assertion/deassertion order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-apple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-exynos.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-exynos.c

## Purpose
`dwc3-exynos.c` is the Samsung Exynos/Google GS101 DWC3 wrapper. It enables SoC-specific clocks and regulators, populates the child DWC3 core from device tree, and handles simple system suspend/resume by disabling/enabling those resources.

## Important APIs, Types, and Functions
The driver uses `struct dwc3_exynos_driverdata` to describe clock names, count, and the suspend clock index for each compatible. `struct dwc3_exynos` stores clock handles and `vdd33`/`vdd10` regulators. Core functions are `dwc3_exynos_probe()`, `dwc3_exynos_remove()`, `dwc3_exynos_suspend()`, and `dwc3_exynos_resume()`.

## Control Flow
Probe gets match data, acquires and enables all named clocks, optionally enables the suspend clock again when a `suspend_clk_idx` is configured, gets and enables `vdd33` then `vdd10`, and calls `of_platform_populate()` to instantiate the child DWC3 core. Error paths disable regulators and clocks in reverse order. Remove depopulates children, disables all clocks, disables the optional suspend clock, then disables regulators.

Suspend disables all clocks and both regulators. Resume enables regulators first, then enables all clocks. The child DWC3 core handles its own PM through the populated child device.

## State and Persistence Behavior
Only live resource handles are stored. There is no retained hardware context in this wrapper; clocks and regulators are restored on resume but wrapper-specific registers are not programmed here. Child core state is owned by the DWC3 child driver.

## Dependencies and Integration Points
Dependencies include OF match data, clk, regulator, platform child population, and system sleep PM. Compatible entries cover multiple Exynos generations and `google,gs101-dwusb3`, each with different clock sets.

## Risks
The suspend clock is enabled in addition to the main clock loop but remove/error handling may disable it separately, so reference counting must match clock provider semantics. Resume error paths can leave `vdd33` enabled if `vdd10` fails, and can leave regulators enabled if a later clock enable fails. Missing device node fails probe because this wrapper only supports OF child population.

## Test Signals
Probe on each compatible should confirm all clock names match bindings and both regulators enable. Suspend/resume should preserve child DWC3 operation and avoid clock/regulator imbalance warnings. Remove/reprobe should not leak child devices. Fault-injection of regulator/clock failures would validate unwind behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-exynos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-generic-plat.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-generic-plat.c

## Purpose
`dwc3-generic-plat.c` is a generic flattened platform wrapper for SoCs that embed a DWC3 core but need only common reset/clock handling plus small per-compatible hooks. It embeds `struct dwc3` and calls `dwc3_core_probe()` directly instead of populating a child `snps,dwc3` node.

## Important APIs, Types, and Functions
`struct dwc3_generic` stores the embedded core, bulk clocks, and reset array. `struct dwc3_generic_config` supplies optional `init()` and `dwc3_properties`. Platform hooks include `dwc3_eic7700_init()` for ESWIN HSP syscon programming and `dwc3_spacemit_k1_init()` for optional host VBUS regulator enable. Main functions are `dwc3_generic_probe()`, `dwc3_generic_remove()`, `dwc3_generic_suspend()`, `dwc3_generic_resume()`, and runtime PM wrappers.

## Control Flow
Probe allocates state, gets the MMIO resource, asserts/deasserts resets with a short delay, registers a devm reset-assert cleanup, enables all clocks with `devm_clk_bulk_get_all_enabled()`, fills `dwc3_probe_data` with `ignore_clocks_and_resets = true`, applies match-data properties and optional init hook, then calls `dwc3_core_probe()`. Remove calls `dwc3_core_remove()`. System suspend calls `dwc3_pm_suspend()` then disables bulk clocks; resume enables clocks then calls `dwc3_pm_resume()`. Runtime PM delegates to exported DWC3 runtime helpers.

## State and Persistence Behavior
State is the embedded `struct dwc3`, reset handle, and bulk clock array. Reset cleanup is devm-managed. No persistent storage exists. Platform syscon writes for EIC7700 and VBUS regulator state for Spacemit are live hardware state only.

## Dependencies and Integration Points
The file integrates reset arrays, bulk clocks, optional regulators, syscon/regmap, OF match data, and DWC3 core PM/probe APIs. Configured compatibles include Spacemit K1/K3, Freescale LS1028A with `gsbuscfg0_reqinfo`, ESWIN EIC7700, and StarFive JHB100.

## Risks
Because this wrapper tells the core to ignore clocks/resets, it must keep clock and reset sequencing correct for every compatible. `devm_clk_bulk_get_all_enabled()` couples acquisition and enable, so suspend/resume must match bulk clock state. Per-compatible init hooks are small but hardware-specific; syscon phandle argument count and offsets must match bindings. If `dwc3_core_probe()` partially initializes, unwind depends on devm and core error paths.

## Test Signals
Test probe/remove and system/runtime PM on each compatible, reset assertion at detach, host VBUS regulator behavior on Spacemit host mode, EIC7700 syscon bit programming, LS1028A GSBUSCFG0 request-info propagation, and clock state after repeated suspend/resume cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-generic-plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-google.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-google.c

## Purpose
`dwc3-google.c` is a Google LGA DWC3 glue driver. It wraps the core with Google-specific resets, clocks, power-domain links, syscon-controlled host PMU/USB interrupt registers, optional USB2-only programming, and host hibernation wake through PME interrupts.

## Important APIs, Types, and Functions
`struct dwc3_google` embeds `struct dwc3` and stores bulk clocks, four resets, non-sticky reset, power-domain devices/links, notifier, syscon offsets, PME IRQs, and hibernation flags. Key functions are `dwc3_google_pm_domain_init()`, `dwc3_google_pm_domain_deinit()`, `dwc3_google_rst_init()`, `dwc3_google_set_pmu_state()`, `dwc3_google_clear_pme_irqs()`, `dwc3_google_enable_pme_irq()`, `dwc3_google_disable_pme_irq()`, `dwc3_google_resume_irq()`, `dwc3_google_usb_psw_pd_notifier()`, `dwc3_google_probe()`, remove, and PM wrappers.

## Control Flow
Probe attaches `psw` and `top` power domains, registers a genpd notifier for hibernation state changes, creates device links, resolves `google,usb-cfg-csr` syscon offsets, sets USB2-only mode if no `usb3-phy` name exists, enables all clocks, gets/deasserts resets, requests disabled-by-default HS/SS PME IRQs, marks wake capable, and calls `dwc3_core_probe()` with clocks/resets ignored by the core.

Suspend first lets the DWC3 core suspend. If in host mode and runtime suspend or wake-capable system suspend applies, it enters hibernation by holding the top power domain active, enabling wake on it, enabling PME IRQs, and setting `is_hibernation`. The `psw` power-domain notifier moves the PMU to D3 and asserts non-sticky reset on domain off, then clears PME, deasserts reset, and returns PMU to D0 on domain on. Non-hibernation suspend asserts resets and disables clocks. Resume reverses hibernation or reenables clocks/resets and then resumes the core.

## State and Persistence Behavior
Live state includes PM domain links, notifier registration, reset state, syscon PMU state, PME IRQ enable/wake state, and `is_hibernation`. USB2-only configuration may need reprogramming after non-hibernation resume. No disk persistence exists.

## Dependencies and Integration Points
The driver depends on clk bulk APIs, reset bulk APIs, genpd attach/notifier/device links, syscon/regmap, IRQ wake, DWC3 core PM, and platform IRQ/resource lookup. It directly resumes the xHCI child device from the PME IRQ if host hibernation wake is valid.

## Risks
PM sequencing is complex. PME IRQs must only be enabled during hibernation, top/psw power-domain links must avoid unintended power collapse, and PMU D0/D3 polling can time out. Non-sticky reset transitions in the genpd notifier happen while power domains change. USB2-only programming must be restored after resets. Error paths must deinit power domains and assert resets consistently.

## Test Signals
Validate probe with both USB2-only and USB3 PHY configurations, PM domain attach/link behavior, hibernation enter/exit, HS and SS PME wake, xHCI resume on PME, PMU D0/D3 poll success, runtime PM cycles, non-wakeup system suspend that asserts resets/clocks off, and remove while domains and IRQs are registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-google.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-haps.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-haps.c

## Purpose
`dwc3-haps.c` is a PCI glue driver for Synopsys HAPS DWC3/USB3 prototyping boards. It turns a PCI function into a child `dwc3` platform device with memory and IRQ resources plus software properties needed by the common core.

## Important APIs, Types, and Functions
`struct dwc3_haps` stores the child platform device and PCI device. `initial_properties` supplies `snps,usb3_lpm_capable`, `snps,has-lpm-erratum`, `snps,dis_enblslpm_quirk`, and `linux,sysdev_is_parent` through `dwc3_haps_swnode`. Main functions are `dwc3_haps_probe()` and `dwc3_haps_remove()`.

## Control Flow
Probe enables the PCI device with managed PCI helpers, sets bus master, allocates private state, allocates a `dwc3` platform device, builds two resources from PCI BAR0 and PCI IRQ, adds resources to the child, sets the PCI device as parent, attaches the software node, adds the platform device, and stores driver data. On failure it removes the software node and drops the platform device. Remove removes the software node and unregisters the child.

## State and Persistence Behavior
State is limited to the child platform device pointer and PCI pointer. The child DWC3 core owns controller runtime state after platform-device registration. No persistent storage exists.

## Dependencies and Integration Points
The driver integrates the PCI subsystem, platform device creation, software nodes/properties, and the common `dwc3` platform driver. PCI IDs cover Synopsys HAPS USB3, HAPS USB3 AXI, and HAPS USB31 devices, with a class mask on one ID to avoid binding unrelated i.MX PCIe controllers sharing VID/PID.

## Risks
Resource translation must be correct because BAR0 is passed directly to the common core. Software-node properties change core behavior globally for this child, especially LPM erratum and ENBLSLPM quirk. Incorrect PCI class matching could bind non-USB hardware. Cleanup must remove the software node before unregistering or dropping the child.

## Test Signals
Test PCI probe/remove on all IDs, child `dwc3` platform probe, BAR and IRQ visibility in the child, DMA through the PCI parent due to `linux,sysdev_is_parent`, class-mask non-match on known conflicting controllers, and no software-node leak across reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-haps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-imx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-imx.c

## Purpose
`dwc3-imx.c` is the NXP i.MX8MP DWC3 glue driver. It embeds the DWC3 core, configures i.MX glue and wakeup registers, manages HSIO/suspend clocks, provides wake IRQ handling, adds xHCI software quirks, and coordinates platform wake behavior with DWC3 runtime/system PM.

## Important APIs, Types, and Functions
`struct dwc3_imx` embeds `struct dwc3` and stores blkctl/glue MMIO, clocks, wake IRQ, PM flags, and board-property bits. Key functions are `dwc3_imx_get_property()`, `dwc3_imx_configure_glue()`, `dwc3_imx_wakeup_enable()`, `dwc3_imx_wakeup_disable()`, `dwc3_imx_interrupt()`, glue callback `dwc3_imx_pre_set_role()`, `dwc3_imx_probe()`, remove, `dwc3_imx_suspend()`, `dwc3_imx_resume()`, runtime PM wrappers, and system PM wrappers.

## Control Flow
Probe reads board properties for permanent attachment, port-power control, over-current polarity, and power polarity; maps `blkctl`, optional `glue`, and `core` resources; enables `hsio` and `suspend` clocks; requests a no-auto-enable wake IRQ; adds a software node with xHCI quirks; configures glue registers; initializes embedded `struct dwc3` with `dwc3_imx_glue_ops`; sets `needs_full_reinit`; calls `dwc3_core_probe()`; and marks the device wake-capable.

The wake IRQ only acts while `pm_suspended`; it disables itself, records `wakeup_pending`, and resumes either the xHCI child or the DWC3 device depending on role. Runtime/system suspend first delegates to DWC3 core PM, then enables wrapper wake sources and IRQ. System suspend additionally enables IRQ wake and out-of-band wake when allowed, or disables suspend clock when not wake-capable, and disables HSIO. Resume reenables clocks, disables IRQ wake, disables wrapper wake, restores glue configuration, handles pending wake accounting/delay, then resumes the DWC3 core.

## State and Persistence Behavior
Live state includes board property bits, `pm_suspended`, `wakeup_pending`, clock state, wake registers, glue registers, and embedded DWC3 state. Glue settings may be lost on power loss and are restored on resume. No disk persistence exists.

## Dependencies and Integration Points
The driver depends on platform named resources, clk, threaded IRQ, OF/platform, runtime PM, software nodes, DWC3 core APIs, and `dwc3_glue_ops`. The `pre_set_role` callback adjusts DWC3 autosuspend behavior: host mode disables core autosuspend to avoid missing xHCI connection events; non-host mode restores autosuspend.

## Risks
Wake handling is timing-sensitive. Host autosuspend is deliberately disabled on role change to avoid missed connection events, and resume inserts a delay for xHCI clock switching after wake. IRQ enable/disable and `wakeup_pending` must remain balanced across runtime and system PM. Optional glue resource absence reduces board configuration. Full reinit requirement means system PM paths must tolerate lost core state.

## Test Signals
Test probe with and without glue resource, all board property combinations, host/device role switches and autosuspend policy, runtime suspend wake from DP/DM and SS connect, system wake with and without device wake capability, pending-wake path for gadget and xHCI, clock disable/enable ordering, glue register restoration after suspend, and remove/reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-imx.c -->
