# sources/distributed-fs/ceph-client/tools/perf/util/include/dwarf-regs.h

Purpose: central declaration point for converting architecture register names and perf register numbers to DWARF register numbers, and for mapping DWARF register numbers to ftrace register strings when libdw support is available.

Important APIs and types: defines missing ELF machine constants for AArch64, C-SKY, and LoongArch; computes `EM_HOST` and `EF_HOST` from compiler architecture macros; defines sentinel pseudo-registers `DWARF_REG_PC` and `DWARF_REG_FB`. With `HAVE_LIBDW_SUPPORT`, it declares `get_dwarf_regstr()`, `get_dwarf_regnum()`, `get_dwarf_regnum_for_perf_regnum()`, architecture-specific conversion helpers, and `get_powerpc_regs()`. Without libdw, it provides inline no-op/failure fallbacks for `get_dwarf_regnum()` and `get_powerpc_regs()`.

Control flow: architecture selection happens at compile time. Runtime dispatch is delegated to implementation files through `machine`/`flags` arguments and architecture-specific helper functions.

State and persistence: none in this header. Conversions are deterministic from architecture, ABI flags, and input register name/number.

Dependencies and integration: includes `annotate.h` and `<elf.h>`, and integrates with perf annotation, probe, unwinding, and register display code. C-SKY ABI flags are handled explicitly because register numbering differs by ABI.

Risks: host architecture detection can fall back to `EM_NONE` on new architectures, reducing feature support. Stub fallbacks under no-libdw builds return failure, so callers must handle missing DWARF conversion. Mismatched ELF flags can yield wrong register mappings.

Test signals: architecture-specific conversion tests, no-libdw build tests, probe/annotation tests that resolve register operands, and cross-build coverage for every `EM_HOST` branch.
