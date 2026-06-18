
# sources/distributed-fs/ceph-client/tools/perf/util/parse-regs-options.c

Purpose: parses `perf record` register sampling option strings for user registers and interrupt registers.

Important APIs/types/functions: `list_perf_regs` prints available register names for a mask. `name_to_perf_reg_mask` resolves a case-insensitive register name to one or more mask bits by calling architecture `perf_reg_name`. `__parse_regs` implements shared parsing for user and interrupt modes. Public callbacks are `parse_user_regs` and `parse_intr_regs`.

Control flow: the parser rejects unset/double-set cases, obtains the architecture mask through `perf_user_reg_mask` or `perf_intr_reg_mask`, defaults to the whole mask when the option has no argument, splits comma-separated names, prints available names for `?`, and ORs matched register bits into the caller mask. Unknown names produce a UI warning suggesting the relevant option with `?`.

State and persistence: only mutates the caller-provided `uint64_t` mask. No global state.

Dependencies: DWARF/ELF machine constants, perf register abstraction, UI warnings/debug, subcmd parse-options, and architecture register-name tables.

Integration points: perf record option handling for sampled user/interrupt register sets. It depends on files under `perf-regs-arch` for architecture masks/names.

Risks: duplicate architecture names are suppressed only in listing; name lookup can return multiple bits when aliases exist. Header/mask consistency is architecture-sensitive. Test signals include `perf record --user-regs=?`, valid/invalid register lists per architecture, no-argument defaults, and double-set rejection.
