## sources/distributed-fs/ceph-client/arch/mips/ath79/common.h

Purpose: small local header for ATH79 common definitions shared by setup and common code.

Important APIs and definitions: `ATH79_MEM_SIZE_MIN` is 2 MiB and `ATH79_MEM_SIZE_MAX` is 256 MiB, used as scan bounds for memory detection. `ath79_ddr_ctrl_init()` is declared for setup code.

Control flow: none.

State and persistence: none directly.

Dependencies and integration: includes `linux/types.h` and is used by `setup.c`, `common.c`, `clock.c`, and `prom.c` as a local interface. The memory bounds feed `detect_memory_region()`.

Risks: incorrect memory bounds would truncate or over-scan RAM detection across all ATH79 boards. The header intentionally exposes only a minimal subset; other globals are declared in public machine headers.

Test signals: boot memory size detection should fall within these bounds. Compile coverage verifies the DDR init declaration.
