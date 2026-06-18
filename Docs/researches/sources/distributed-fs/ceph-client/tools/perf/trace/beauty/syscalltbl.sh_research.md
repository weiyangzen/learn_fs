# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/syscalltbl.sh

Purpose: Generates C syscall-number lookup tables for all supported architectures.

Important APIs/types/functions: `build_tables` reads one syscall table and emits `syscall_num_to_name_<machine>[]` and `syscall_sorted_names_<machine>[]`. `build_outer_table` emits entries for the final `static const struct syscalltbl syscalltbls[]`.

Control flow: The script validates two arguments, removes the output file, writes common C definitions, then conditionally appends table definitions for alpha, arm, arm64, csky, mips, parisc, powerpc, riscv, s390, sh, sparc, x86, xtensa, and a generic `EM_NONE`. `build_tables` filters table rows by ABI, sorts by number for direct lookup, and sorts by padded syscall name for binary/name lookup behavior consistent with runtime string comparison.

State and persistence: It writes directly to the requested output header and uses a temporary file for sorted intermediate rows.

Dependencies and integration points: Consumed by perf trace syscall name resolution. Depends on kernel `tools/perf/arch/*/entry/syscalls` tables, `scripts/syscall.tbl`, `grep`, `sort`, `awk`, and `sed`.

Risks: Direct output writes are not atomic. ABI filter lists must track kernel table changes. The name-padding sort workaround is fragile for unusual names.

Test signals: Run generator with the tools directory and compile the generated header under native and `ALL_SYSCALLTBL` builds; verify number-to-name and sorted-name lookups for representative architectures.
