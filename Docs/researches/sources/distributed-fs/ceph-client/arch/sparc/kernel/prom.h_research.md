# sources/distributed-fs/ceph-client/arch/sparc/kernel/prom.h

Purpose: small internal header shared by SPARC PROM/device-tree builders. It exposes the console initialization hook and early PROM allocation accounting.

Important APIs/types/functions: declares `of_console_init()` and `extern unsigned int prom_early_allocated`; includes Linux spinlocks and architecture PROM declarations needed by PROM implementation files.

Control flow: no runtime logic is present. The header coordinates compile-time visibility between `prom_common.c` and the 32-bit/64-bit PROM implementations.

State and persistence: `prom_early_allocated` is an init-time byte counter for allocations made while constructing the device tree and console metadata. It is not persistent after boot.

Dependencies and integration points: integrates with Open Firmware PROM code, `of_pdt_build_devicetree()`, and architecture-specific `prom_early_alloc()` definitions.

Risks: declarations must remain consistent with both SPARC32 and SPARC64 implementations. Changing the allocation counter type or lifetime would affect boot diagnostics.

Test signals: successful SPARC boot device-tree construction, console initialization, and a sane `PROM: Built device tree with ... bytes` message from `prom_common.c`.
