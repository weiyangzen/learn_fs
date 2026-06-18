# sources/distributed-fs/ceph-client/drivers/memory/stm32-fmc2-ebi.c

Purpose: STM32 FMC2 External Bus Interface driver configuring SRAM, PSRAM, NOR, and NAND chip-select resources from device-tree child nodes. It translates bus/timing properties into FMC2 registers, handles STM32MP1 versus STM32MP25 register differences, restores setup after sleep, and populates child devices.

Important APIs/types/functions: `struct stm32_fmc2_ebi_data` supplies per-SoC property tables, enable register/bit, setup save/restore callbacks, optional RIF access checks, and semaphore callbacks. `struct stm32_fmc2_ebi` stores device, clock, regmap, bank assignment, security access, semaphore bitmap, and saved register values. `struct stm32_fmc2_prop` describes one DT property, including validation, timing conversion, and setter callbacks. Major helpers include transaction-type setup, bus-width/cache-size setters, timing conversion, `stm32_fmc2_ebi_mp25_check_rif()`, `stm32_fmc2_ebi_parse_dt()`, probe/remove, and PM callbacks.

Control flow: probe gets a syscon regmap from the node, clock, optional reset, enables runtime PM, resets hardware, checks MP25 RIF/secure access, parses each available child `reg`, rejects duplicate/invalid banks, optionally acquires semaphores, configures EBI chip selects, marks assigned banks, verifies NWAIT sharing on MP1, enables FMC2, populates children, and saves setup. Each chip select is disabled while its property table is applied, then re-enabled. Suspend disables FMC2, releases semaphores, runtime-suspends the clock, and selects sleep pins. Resume reacquires semaphores, restores saved registers, and re-enables FMC2.

State and persistence: runtime state includes assigned bank bitmap, saved BCR/BTR/BWTR/PCSCNTR/CFGR values, access-granted flag, and taken MP25 semaphores. Hardware state is the actual FMC2 bus configuration and resource isolation state. State is preserved only in kernel memory across sleep.

Dependencies and integration: uses regmap, runtime PM, clock/reset, pinctrl sleep states, OF child parsing, `of_platform_populate()`, and STM32 MP25 RIF/semaphore register conventions. It supports compatibles `st,stm32mp1-fmc2-ebi` and `st,stm32mp25-fmc2-ebi`.

Risks: property descriptors are order-sensitive because transaction type must be parsed first. Validation callbacks silently skip unsupported optional properties, which can mask DT mistakes. MP25 secure/CID/semaphore behavior can leave access read-only if CFGR is secure. Timing conversion depends on a nonzero HCLK rate. NWAIT cannot be shared between EBI and NAND on MP1. Error cleanup must release semaphores and disable configured banks.

Test signals: validate DTs for each transaction type, 8/16-bit buses, cclk and mux modes, async/sync timing properties, MP1 NWAIT with NAND conflict, MP25 secure and semaphore access-denied paths, suspend/resume register restoration, child population, and runtime PM clock enable/disable.
