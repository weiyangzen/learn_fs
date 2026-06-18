# sources/distributed-fs/ceph-client/include/soc/at91/at91sam9_sdramc.h

Purpose: defines register offsets and bit masks for AT91SAM9 SDRAM Controller system peripheral registers.

Important APIs and types: macros cover mode, refresh timer, configuration, low-power, interrupt enable/disable/mask/status, and memory device registers. Fields encode command mode, column/row/bank geometry, CAS latency, data bus width, timing delays, low-power mode, partial array self-refresh, temperature compensation, drive strength, timeout, refresh error status, and SDRAM/low-power SDRAM type.

Control flow: board or memory-controller initialization code writes configuration/timing fields, sequences SDRAM command modes through the mode register, sets refresh, and handles or masks refresh-error interrupts.

State and persistence: only live controller MMIO state is described. Runtime persistence is the configured SDRAM mode until reset/suspend reprogramming.

Dependencies and integration points: standalone header integrated by AT91 platform memory and power-management code.

Risks and test signals: risks include wrong geometry causing aliasing/corruption, invalid timing at changed clock rates, low-power mode misconfiguration, and unhandled refresh errors. Test boot memory sizing, memtest under load, low-power transitions, refresh interrupt paths, and compile coverage for legacy AT91SAM9 boards.
