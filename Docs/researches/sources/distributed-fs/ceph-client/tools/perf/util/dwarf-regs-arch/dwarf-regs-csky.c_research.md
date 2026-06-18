# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-csky.c

Purpose: Implements C-SKY DWARF register name and perf-register mapping for both ABI v1 and ABI v2. `__get_csky_regstr(n, flags)` returns a `%reg` name from ABI-specific tables, `__get_csky_regnum(name, flags)` performs reverse lookup, and `__get_dwarf_regnum_for_perf_regnum_csky(perf_regnum, flags)` maps perf enums to ABI-specific DWARF numbers.

Control flow and state: Stateless table lookups. `EF_CSKY_ABIV2` selects the ABI v2 table/column; otherwise ABI v1 is used. Missing entries are encoded as NULL or `-ENOENT`.

Dependencies and integration: Forces `__CSKYABIV2__` before including C-SKY perf register uapi definitions. Integrated by `dwarf-regs.c` for `EM_CSKY`, which passes ELF flags through to preserve ABI selection.

Risks: Sparse tables and TODO entries mean several perf registers intentionally cannot be translated. The bounds check uses `perf_regnum > ARRAY_SIZE(...)`; an index exactly equal to `ARRAY_SIZE` is risky and should be scrutinized because valid C arrays require `< ARRAY_SIZE`.

Test signals: ABI v1/v2 lookup tests for stack, link, argument, extended, PC/EPC, and unsupported registers; reverse lookup tests for NULL holes; ELF-flag integration tests.
