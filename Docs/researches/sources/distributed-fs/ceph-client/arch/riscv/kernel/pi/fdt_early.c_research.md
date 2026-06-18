# sources/distributed-fs/ceph-client/arch/riscv/kernel/pi/fdt_early.c

Purpose: Performs early FDT parsing for KASLR seed discovery, ISA extension matching, and SATP mode selection.

Important APIs/types/functions: Implements `get_kaslr_seed()`, `fdt_early_match_extension_isa()`, `set_satp_mode_from_fdt()`, and helpers for node availability, node-name checks, and ISA-string extension matching.

Control flow: Early boot reads `/chosen/kaslr-seed`, checks CPU nodes for availability and requested ISA extensions, parses memory/MMU-related properties, and chooses supported page-table mode before normal OF code is available.

State and persistence: No file-local persistent state; returns seed and SATP decisions to early boot. Consumes immutable FDT data.

Dependencies and integration points: Depends on libfdt, early command-line parsing, KASLR, page table mode setup, and ISA extension naming conventions.

Risks and test signals: Early parsing must be robust against malformed FDTs and heterogeneous CPU nodes. Test missing seed, Zkr fallback, disabled CPU nodes, ISA extension string variants, and page-mode restrictions.
