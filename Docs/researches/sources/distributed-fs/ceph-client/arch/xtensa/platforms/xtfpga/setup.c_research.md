# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/setup.c

## Purpose
`setup.c` provides XTFPGA board setup: restart and power-off handlers, optional CPU counter calibration, Open Firmware clock and MAC-address fixups, and legacy non-DT platform device registration for Ethernet, USB, and UART.

## Important APIs, types, and functions
- `xtfpga_power_off()` displays `POWEROFF`, disables interrupts, and spins.
- `xtfpga_restart()` writes the software-reset register and falls back to `cpu_reset()`.
- `platform_calibrate_ccount()` reads the FPGA clock-frequency register into `ccount_freq` when `CONFIG_XTENSA_CALIBRATE_CCOUNT` is enabled.
- `xtfpga_clk_setup()` implements `CLK_OF_DECLARE(..., "cdns,xtfpga-clock", ...)` by reading a fixed-rate clock from MMIO.
- `update_local_mac()` copies a DT `local-mac-address` property and replaces the last byte with DIP-switch bits.
- `machine_setup()` is the DT initcall; `xtavnet_init()` is the non-DT initcall registering `ethoc`, `c67x00`, and `serial8250` devices.

## Control flow
Both DT and non-DT paths call `xtfpga_register_handlers()` during `arch_initcall`. In DT builds, clock setup is driven by early OF clock matching, then `machine_setup()` patches the first `opencores,ethoc` node's MAC property. In non-DT builds, static resource arrays describe Ethernet register/buffer/IRQ ranges, USB HPI resources, and DUART16552 serial resources; `xtavnet_init()` fills DIP-switch MAC and clock-dependent fields before `platform_add_devices()`.

## State and persistence behavior
The restart/power-off handlers persist in the kernel sys-off handler registry. DT MAC patching allocates a replacement `struct property` and string name that become owned by the live device tree. Non-DT platform devices and their platform data remain static for the life of the kernel. Hardware state changes include reset-register writes, LCD text, DIP-switch reads, and clock-frequency reads.

## Dependencies and integration points
This file integrates with Linux sys-off, clock provider, OF address/property APIs, Xtensa `cpu_reset()`, XTFPGA hardware constants, the LCD helper, OpenCores `ethoc`, Cypress `c67x00`, and 8250 serial. Endianness-sensitive values come from `XCHAL_HAVE_BE` in variant headers.

## Risks and edge cases
`xtfpga_restart()` assumes the magic software-reset write is sufficient or that jumping through `cpu_reset()` is safe with devices still active. `update_local_mac()` leaks the allocated property intentionally into the OF tree but must allocate both value and name successfully. The non-DT path truncates DIP switches into the last MAC byte without masking, unlike the DT path's `& 0x3f`. Resource constants must match the FPGA bitstream.

## Test signals
Relevant signals are DT boot with a `cdns,xtfpga-clock` node, Ethernet MAC last-byte updates from DIP switches, non-DT registration of `ethoc`, `c67x00`, and `serial8250`, reboot via sys-off, and poweroff LCD/spin behavior. Build tests should cover `CONFIG_USE_OF`, non-OF, and `CONFIG_XTENSA_CALIBRATE_CCOUNT`.
