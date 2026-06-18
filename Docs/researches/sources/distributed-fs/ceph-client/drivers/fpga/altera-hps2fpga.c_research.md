## sources/distributed-fs/ceph-client/drivers/fpga/altera-hps2fpga.c

Purpose: this driver manages Altera SoCFPGA bridges between the host processor system and FPGA fabric: HPS-to-FPGA, lightweight HPS-to-FPGA, and FPGA-to-HPS. It enables/disables bridges by reset control and, for HPS-visible bridges, updates L3 remap visibility bits.

Important APIs and functions: `struct altera_hps2fpga_data` carries bridge name, reset control, optional L3 regmap and remap mask, and clock. `_alt_hps2fpga_enable_set()` asserts or deasserts bridge reset and updates the write-only L3 remap register through a global shadow protected by `l3_remap_lock`. FPGA bridge callbacks are `alt_hps2fpga_enable_set()` and `alt_hps2fpga_enable_show()`.

Control flow: OF match data provides one of three static bridge templates. Probe obtains an exclusive reset control, optional `altr,l3regs` syscon for remapped bridges, a clock, enables the clock, optionally applies `bridge-enable`, registers the FPGA bridge, and stores it as driver data. Remove unregisters the bridge and disables the clock.

State and persistence: bridge state is mostly hardware reset state plus `l3_remap_shadow` because the L3 remap register is write-only. The static match-data structures are mutated per probed device, so each compatible effectively shares template storage.

Dependencies and integration: it integrates with reset controller, clock framework, syscon/regmap, OF property APIs, and FPGA bridge framework. FPGA regions rely on these bridges to isolate fabric from HPS traffic before reconfiguration.

Risks: static match-data mutation can be fragile if multiple devices of the same compatible exist, because fields such as reset, regmap, and clock are shared. `enable_show()` returns `reset_control_status()`, whose semantics may be reset-asserted rather than bridge-enabled depending on reset provider. L3 shadow starts at zero and may not reflect bootloader state until a bridge operation occurs. Missing `bridge-enable` leaves hardware in its existing state.

Test signals: cover all three compatibles, clock/reset failure unwinds, remap shadow updates under concurrent bridge toggles, `bridge-enable` application, and repeated enable/disable cycles while checking L3 visibility and reset status.
