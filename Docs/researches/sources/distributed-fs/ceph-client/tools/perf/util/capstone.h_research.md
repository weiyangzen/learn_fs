# sources/distributed-fs/ceph-client/tools/perf/util/capstone.h

Purpose: declares Capstone-backed disassembly entry points and no-op stubs when Capstone support is unavailable.

Important APIs/types: `capstone__fprintf_insn_asm`, `symbol__disassemble_capstone`, and `symbol__disassemble_capstone_powerpc`; unsupported builds inline-return `-1`.

Control flow: callers can invoke the functions unconditionally and treat `-1` as unsupported/fallback-required.

State and persistence: no header state.

Dependencies and integration: forward-declares annotation, machine, symbol, and thread types; gates optional Capstone integration for annotate and instruction printing.

Risks: fallback behavior relies on consistent caller interpretation of `-1`.

Test signals: compile with and without `HAVE_LIBCAPSTONE_SUPPORT` and verify annotate fallback behavior.
