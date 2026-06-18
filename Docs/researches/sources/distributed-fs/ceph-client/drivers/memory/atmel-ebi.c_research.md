# sources/distributed-fs/ceph-client/drivers/memory/atmel-ebi.c

## Purpose
`atmel-ebi.c` is the platform driver for Atmel/Microchip external bus interface controllers. It configures Static Memory Controller timings and modes for child devices described in device tree and restores those configurations on resume.

## Important APIs, Types, And Functions
Important types are `struct atmel_ebi`, `struct atmel_ebi_dev`, `struct atmel_ebi_dev_config`, and `struct atmel_ebi_caps`. The caps table provides available chip selects, optional EBI CSA register offset, syscon phandle name, and get/xlate/apply callbacks. Core functions include `atmel_ebi_xslate_smc_timings()`, `atmel_ebi_xslate_smc_config()`, `atmel_ebi_dev_setup()`, `atmel_ebi_dev_disable()`, `atmel_ebi_probe()`, and `atmel_ebi_resume()`.

## Control Flow
Probe allocates driver state, gets the EBI clock, resolves the `atmel,smc` syscon/regmap/layout/clock, optionally resolves the matrix or SFR regmap for EBICSA, reads address and size cell counts, and iterates available child nodes with `reg`. Each child setup validates chip-select entries against SoC capabilities, translates any `atmel,smc-*` timing/mode properties, applies config to all chip selects when present, reads back config into persistent per-child records, optionally clears EBICSA bits to attach the child to generic SMC logic, and records the child for resume. On child setup failure, the child device tree node is marked disabled before population.

## State And Persistence
Runtime state stores clocks, regmaps, SoC caps, and a list of configured child devices with read-back SMC configs. Hardware state is persisted in SMC and optional matrix/SFR registers. Resume replays saved per-chip-select configs. The driver is built in through `builtin_platform_driver_probe()`.

## Dependencies And Integration Points
The driver depends on OF, platform bus, syscon/regmap, Atmel SMC MFD helpers, Atmel matrix/SFR definitions, and child device population. It is selected by `CONFIG_ATMEL_EBI` and supports multiple AT91/SAMA5/SAM9X60 compatible strings through per-SoC caps.

## Risks And Test Signals
Risks include incomplete timing property groups, clock-rate conversion overflow or truncation, invalid `reg` cell parsing, leaking enabled SMC clocks on probe errors after enable, incorrect EBICSA bit handling, and resume replay after partial child setup. Tests should cover device trees with single and multiple chip selects, absent versus complete SMC properties, all bus widths/page modes/read-write modes, invalid chip selects, SAMA5 HSMC versus AT91 SMC paths, probe deferral/error paths, and suspend/resume register restoration.
# sources/distributed-fs/ceph-client/drivers/memory/atmel-ebi.c

## Purpose
`atmel-ebi.c` is the platform driver for Atmel/Microchip external bus interface controllers. It configures Static Memory Controller timings and modes for child devices described in device tree and restores those configurations on resume.

## Important APIs, Types, And Functions
Important types are `struct atmel_ebi`, `struct atmel_ebi_dev`, `struct atmel_ebi_dev_config`, and `struct atmel_ebi_caps`. The caps table provides available chip selects, optional EBI CSA register offset, syscon phandle name, and get/xlate/apply callbacks. Core functions include `atmel_ebi_xslate_smc_timings()`, `atmel_ebi_xslate_smc_config()`, `atmel_ebi_dev_setup()`, `atmel_ebi_dev_disable()`, `atmel_ebi_probe()`, and `atmel_ebi_resume()`.

## Control Flow
Probe allocates driver state, gets the EBI clock, resolves the `atmel,smc` syscon/regmap/layout/clock, optionally resolves the matrix or SFR regmap for EBICSA, reads address and size cell counts, and iterates available child nodes with `reg`. Each child setup validates chip-select entries against SoC capabilities, translates any `atmel,smc-*` timing/mode properties, applies config to all chip selects when present, reads back config into persistent per-child records, optionally clears EBICSA bits to attach the child to generic SMC logic, and records the child for resume. On child setup failure, the child device tree node is marked disabled before population.

## State And Persistence
Runtime state stores clocks, regmaps, SoC caps, and a list of configured child devices with read-back SMC configs. Hardware state is persisted in SMC and optional matrix/SFR registers. Resume replays saved per-chip-select configs. The driver is built in through `builtin_platform_driver_probe()`.

## Dependencies And Integration Points
The driver depends on OF, platform bus, syscon/regmap, Atmel SMC MFD helpers, Atmel matrix/SFR definitions, and child device population. It is selected by `CONFIG_ATMEL_EBI` and supports multiple AT91/SAMA5/SAM9X60 compatible strings through per-SoC caps.

## Risks And Test Signals
Risks include incomplete timing property groups, clock-rate conversion overflow or truncation, invalid `reg` cell parsing, leaking enabled SMC clocks on probe errors after enable, incorrect EBICSA bit handling, and resume replay after partial child setup. Tests should cover device trees with single and multiple chip selects, absent versus complete SMC properties, all bus widths/page modes/read-write modes, invalid chip selects, SAMA5 HSMC versus AT91 SMC paths, probe deferral/error paths, and suspend/resume register restoration.
