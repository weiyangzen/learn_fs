# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_scd.h

Purpose: defines BCM1480-family System Control and Debug bitfields. It is the chip-specific supplement to `sb1250_scd.h`, adding new part IDs and the changed SCD layouts for system configuration, watchdog reset targets, performance counters, address traps, and trace control.

Important APIs/types/functions: the file exports only macros. Key constants are `K_SYS_PART_BCM1480`, `K_SYS_PART_BCM1280`, `K_SYS_PART_BCM1455`, `K_SYS_PART_BCM1255`, and `K_SYS_PART_BCM1158`; `M_BCM1480_SYS_*`/`V_BCM1480_SYS_*` fields for PLL, boot mode, node ID, CPU reset/disable, ccNUMA, and reset flags; watchdog reset-type encodings; performance-counter source fields `SRC4` through `SRC7`; address-trap agent IDs; and trace sequence/config additions.

Control flow: platform code reads revision/manufacturing registers, derives SoC identity, configures clocks/boot-mode-dependent peripherals, masks or resets CPUs, arms watchdogs, selects performance-counter events, installs address traps, and configures trace collection. This header supplies the bit encodings for those flows while the actual MMIO addresses come from `bcm1480_regs.h`.

State and persistence: all represented state lives in SCD hardware registers. Some bits are latched status from reset or bus errors; others trigger resets, counter clear/enable operations, watchdog behavior, or trace capture state.

Dependencies and integration: depends on `sb1250_defs.h` plus `sb1250_scd.h` for shared fields. The comments explicitly warn that BCM1480 SCD symbols are distinct from SB1250 `A_SCD_*`/field names; integration should use `_BCM1480_` names when targeting the newer family.

Risks and test signals: reset, watchdog, and CPU-disable masks are high impact. Wrong reset-type or CPU bit selection can reset the wrong core or whole system. Compile tests should cover `SIBYTE_HDR_FEATURE_CHIP(1480)`, and runtime tests should validate part ID decode, timer/watchdog interrupts, per-core reset/mask behavior, performance counter clear/enable, address trap matching, and trace register programming on actual hardware or an accurate simulator.
