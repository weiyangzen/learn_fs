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
