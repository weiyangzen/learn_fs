<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atmel-smc.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/atmel-smc.c

Purpose: provides exported helper functions for configuring Atmel SMC/HSMC chip-select timing registers through a syscon/regmap. It is not a probing driver; it is a shared encoding/apply/get library for memory-controller consumers.

Important APIs and functions: exported functions include `atmel_smc_cs_conf_init`, timing field setters `atmel_smc_cs_conf_set_timing`, `set_setup`, `set_pulse`, `set_cycle`, apply/get helpers for SMC and HSMC, and `atmel_hsmc_get_reg_layout`. Internal `atmel_smc_cs_encode_ncycles` performs the datasheet split-MSB/LSB timing encoding with saturation.

Control flow: consumers initialize `struct atmel_smc_cs_conf`, call setter helpers to encode cycle counts into setup/pulse/cycle/timings fields, then apply the completed config to either legacy SMC register offsets or HSMC layout-based offsets. Getter helpers read current register values back into the same config structure. Layout lookup matches the controller DT node and returns NULL for legacy SMC, a layout pointer for SAMA5D2/D3 HSMC, or `ERR_PTR(-EINVAL)` for unknown nodes.

State and persistence: this file owns no runtime state. It mutates caller-owned config structures and writes persistent hardware controller registers through the supplied regmap.

Dependencies and integration points: depends on exported GPL symbols, OF matching, regmap, and register layout macros from `linux/mfd/syscon/atmel-smc.h`. NAND, memory, or bus drivers use these helpers after acquiring the SMC syscon regmap.

Risks: setter helpers update the encoded field even when returning `-ERANGE`, using the maximum representable value; callers must check the return if exact timing matters. Invalid shift values return `-EINVAL` without changing the relevant field. Apply/get helpers ignore regmap read/write return codes, so bus errors are silent. The function comments for pulse/cycle mention storing in `setup` though the code correctly writes `pulse`/`cycle`.

Test signals: unit-style tests for timing encoding boundaries and saturation, DT layout lookup for at91sam9260/sama5d2/sama5d3 compatibles, regmap write sequences for SMC and HSMC chip selects, consumers checking `-ERANGE`, and hardware memory timing validation with attached NAND/SRAM devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/atmel-smc.c -->
