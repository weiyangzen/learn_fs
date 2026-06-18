## sources/distributed-fs/ceph-client/arch/mips/ath25/devices.h

Purpose: shared ATH25 declarations and helpers for SoC family dispatch, bitfield extraction, global board/SoC state, and common device-registration APIs.

Important APIs and types: `ATH25_REG_MS()` extracts masked/shifted fields by macro naming convention. `ATH25_IRQ_CPU_CLOCK` defines the CP0 timer interrupt. `enum ath25_soc_type` enumerates AR2312/13/5312 and AR2315/16/17/18 plus unknown. Externs expose `ath25_soc`, `ath25_board`, and `ath25_irq_dispatch`. Function prototypes cover config scanning, serial setup, and WMAC registration. `is_ar2315()` checks `current_cpu_data.cputype == CPU_4KEC`; `is_ar5312()` is its negation.

Control flow: none beyond inline CPU-family predicates. Callers use these predicates during boot and initcalls.

State and persistence: none directly; declares global runtime state stored in `devices.c` and `board.c`.

Dependencies and integration: includes `linux/cpu.h`, ATH25 platform structures, and MIPS CPU data. It is included by every ATH25 C file.

Risks: CPU type is the only family discriminator, so unsupported compatible CPUs may be routed incorrectly. `ATH25_REG_MS()` requires fields to provide `_M` and `_S` macros exactly.

Test signals: compile all consumers and boot both CPU families to verify `is_ar2315()` branch selection. WMAC and serial setup depend on these declarations.
