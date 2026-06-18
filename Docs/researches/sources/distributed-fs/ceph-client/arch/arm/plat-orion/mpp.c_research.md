# sources/distributed-fs/ceph-client/arch/arm/plat-orion/mpp.c

Purpose: Applies Marvell Orion multi-purpose pin (MPP) mux configuration tables and synchronizes GPIO valid-direction masks with selected pin functions.

Important functions: `mpp_ctrl_addr()` computes the MMIO address for each MPP control register. `orion_mpp_conf()` reads current control registers, validates requested entries against max pin and variant mask, updates 4-bit mux fields, derives GPIO input/output capability bits, calls `orion_gpio_set_valid()`, and writes final registers.

Control flow/state: The MPP list is zero-terminated. Each register controls eight pins with four bits per pin. Initial and final register values are printed at debug level. Hardware mux registers and GPIO validity state are changed during boot.

Dependencies/integration: Depends on MBus, MMIO, Linux GPIO headers, `plat/mpp.h`, and `plat/orion-gpio.h`. Board-specific pin tables pass SoC variant masks to prevent invalid mux settings.

Risks/tests: The function only warns and continues on unavailable variant entries, which can leave pins in reset/default state while the peripheral driver later probes. `mpp_max` larger than the local eight-register buffer aborts setup. Tests should validate board MPP tables, variant filtering, GPIO validity side effects, and final register dumps against expected values.
