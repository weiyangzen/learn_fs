<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_scd.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_scd.h

Purpose: Defines the Broadcom SiByte SB1250/BCM112x/BCM1480 System Control and Debug register bit layout used by early platform setup, clock/reset handling, watchdog/timer code, performance counters, bus error reporting, address traps, and trace-buffer programming.

Important APIs/types/functions: `M_SYS_*`, `S_SYS_*`, `V_SYS_*`, and `G_SYS_*` macros for system revision, part, SOC type, manufacturing, and system configuration fields; revision constants such as `K_SYS_REVISION_BCM1250_C0`; `SYS_SOC_TYPE`; watchdog and timer constants `V_SCD_WDOG_FREQ`, `M_SCD_WDOG_*`, `V_SCD_TIMER_FREQ`, `M_SCD_TIMER_*`; bus/ECC fields `S_SCD_BERR_*`, `S_SCD_L2ECC_*`, `S_SCD_MEM_ECC_*`; address trap fields `M_ATRAP_*`; trace controls `M_SCD_TRACE_CFG_*`, `V_SCD_TREVT_*`, and `V_SCD_TRSEQ_*`.

Control flow: There is no executable control flow apart from macro expressions. Callers read memory-mapped SCD registers, decode fields through the `G_` macros, compose register writes through the `V_` and `M_` macros, and branch on revision/SOC constants. `SYS_SOC_TYPE` has both assembler and C forms and normalizes alternate BCM1250 encodings back to the canonical BCM1250 SOC type.

State and persistence: The file names persistent hardware state rather than owning software state: reset bits, watchdog and timer enable/count values, performance counter source/enable bits, captured bus/ECC error fields, and trace-buffer configuration. Writes through these masks can reset CPUs, trigger soft or system reset, enable watchdog reset behavior, clear trace buffers, or alter diagnostic capture.

Dependencies and integration points: Depends on `asm/sibyte/sb1250_defs.h` for `_SB_MAKE64`, `_SB_MAKEMASK`, `_SB_MAKEVALUE`, and feature-selection macros. Integrated by SiByte board setup, timer, watchdog, interrupt, performance, and low-level debug code that already knows the SCD register addresses.

Risks: Register programming is hardware destructive if masks are applied to the wrong revision; several fields are conditional on `SIBYTE_HDR_FEATURE*`. The header also carries legacy quirks, including duplicate `M_ATRAP_INDEX` and a likely typo in `G_SCD_TREVT_DATAID` referencing `M_SCD_TREVT_DATID`, so build coverage is important when touching trace definitions.

Test signals: Useful signals are MIPS SiByte build coverage, boot on SB1250/BCM112x hardware or emulator, timer/watchdog interrupt tests, reset-path smoke tests, and any diagnostics that read SCD bus/ECC/trace registers.

Source read size: 641 lines, 24159 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_scd.h -->
