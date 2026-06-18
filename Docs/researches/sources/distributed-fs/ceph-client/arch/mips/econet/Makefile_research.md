# sources/distributed-fs/ceph-client/arch/mips/econet/Makefile

Purpose: builds EcoNet platform initialization.

Important behavior: unconditionally includes `init.o` for the EcoNet platform directory.

Dependencies and integration: tied to the top-level architecture platform selection; all runtime behavior lives in `init.c`.

Risks and test signals: minimal build risk. EcoNet platform builds should link `prom_init`, `plat_mem_setup`, IRQ, DT, and timer hooks from `init.o`.
