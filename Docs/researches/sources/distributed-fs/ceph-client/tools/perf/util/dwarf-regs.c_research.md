# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs.c

Purpose: Central architecture dispatcher for translating DWARF register numbers to perf probe register strings, register strings back to DWARF numbers, and perf sample register enums to DWARF frame numbers.

Important APIs: `get_dwarf_regstr(n, machine, flags)` selects an architecture table or C-SKY ABI helper. `get_dwarf_regnum(name, machine, flags)` normalizes a register token and dispatches to arch reverse lookups. `get_dwarf_regnum_for_perf_regnum(perf_regnum, machine, flags, only_libdw_supported)` converts perf enum registers and optionally filters out registers beyond libdw frame support. `get_libdw_frame_nregs` encodes per-architecture libdw frame limits.

Control flow and state: Stateless switch on ELF machine, defaulting `EM_NONE` to `EM_HOST`. Register-string tables are compiled by defining `DEFINE_DWARF_REGSTR_TABLE` before including architecture table headers. Unsupported machines log an error and return NULL or `-ENOENT`.

Dependencies and integration: Includes many arch DWARF register table headers plus arch-specific helpers from `dwarf-regs-arch`. Used by probe argument parsing, DWARF variable decoding, and sample register interpretation.

Risks: `get_dwarf_regnum` duplicates `name` into `regname` and strips trailing delimiters, but dispatches `name` rather than `regname`; this means delimiter stripping is ineffective for current calls and should be reviewed. Architecture switch coverage and libdw register counts must track new ELF machines and libdw support.

Test signals: Cross-architecture table tests for valid/invalid names, delimiter-stripped tokens, `EM_NONE` host fallback, unsupported machine errors, and `only_libdw_supported` filtering for high-number registers.
