## sources/distributed-fs/ceph-client/include/linux/bug.h

**Purpose:** This header centralizes kernel BUG/WARN reporting contracts and data-corruption checking helpers.

**Important APIs/types/functions:** `enum bug_trap_type` classifies trap handling as none, warning, or BUG. `MAYBE_BUILD_BUG_ON()` chooses compile-time or runtime checking depending on constant-ness. With `CONFIG_GENERIC_BUG`, declarations include `bug_get_file_line()`, `find_bug()`, `report_bug()`, `report_bug_entry()`, `is_valid_bugaddr()`, and `generic_bug_clear_once()`, plus `is_warning_bug()`. Without it, safe stubs are provided. `mem_dump_obj()` is printk-gated. `CHECK_DATA_CORRUPTION()` warns or BUGs depending on `CONFIG_BUG_ON_DATA_CORRUPTION`.

**Control flow, state, persistence:** Runtime state is architecture/generic BUG tables and once-warning metadata managed elsewhere. This header selects reporting behavior and exposes helpers that callers must act on, especially `CHECK_DATA_CORRUPTION()` returning a boolean.

**Dependencies/integration:** Includes `asm/bug.h`, compiler helpers, and `build_bug.h`. Integrates with trap handlers, printk, and corruption-hardening code.

**Risks and test signals:** Risks include using BUG where recoverable error handling is required, ignoring the return from corruption checks, and config-specific behavior changes. Test signals include WARN/BUG selftests, objtool/trap-table validation, printk/no-printk builds, and fault-injection paths that confirm corruption detection returns are handled.
