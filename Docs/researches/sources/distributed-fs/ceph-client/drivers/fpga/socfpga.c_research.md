# sources/distributed-fs/ceph-client/drivers/fpga/socfpga.c

Purpose: FPGA manager for earlier Altera SoCFPGA devices. It resets the FPGA, configures passive-parallel width and CDRATIO from MSEL, writes the bitstream through an FPGA data aperture, waits for CONF_DONE through an interrupt-backed completion, generates final DCLKs, and returns the FPGA to user mode.

Important APIs and functions: `struct socfpga_fpga_priv` stores control/data MMIO, a completion, and IRQ number. Helper functions wrap MMIO, read monitor/status state, clear/generate DCLKs, poll state, configure GPIO-style interrupts, get/set configuration mode, and reset. Manager ops are `socfpga_fpga_ops_configure_init`, `socfpga_fpga_ops_configure_write`, `socfpga_fpga_ops_configure_complete`, and `socfpga_fpga_ops_state`. `socfpga_fpga_isr` completes when CONF_DONE and nSTATUS are asserted.

Control flow: probe maps two resources, gets and requests the IRQ, and registers a devm FPGA manager. Write-init rejects partial reconfiguration, sets mode-specific CDRATIO/width and NCE, enables manager control, asserts and releases reset, waits for configuration state, clears nSTATUS interrupt, and enables AXI config data transfer. Write emits complete and tail 32-bit words. Write-complete waits up to ten milliseconds for interrupt completion, disables AXI config, generates four DCLKs, waits for user mode, and disables manager control.

State and persistence: Linux state is MMIO mappings, IRQ handler, and completion. Hardware state includes control bits, MSEL-derived mode, GPIO monitor/status bits, DCLK counters, and configured FPGA fabric. The bitstream itself persists only as supported by the hardware configuration mode.

Dependencies and integration points: depends on platform resources, OF compatible `altr,socfpga-fpga-mgr`, interrupt core, completions, FPGA manager framework, and SoCFPGA register layout.

Risks and test signals: risks include very short polling timeouts, interrupt-only config-done detection, no support for partial reconfiguration, native-endian word streaming, and potential timeout sensitivity under slow hardware. Test signals are IRQ delivery on CONF_DONE, state sysfs moving to operating, correct reset/config/user-mode transitions, data aperture writes, timeout behavior when nSTATUS fails, and successful devm cleanup.
