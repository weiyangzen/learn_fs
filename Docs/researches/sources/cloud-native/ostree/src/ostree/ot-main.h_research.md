# sources/cloud-native/ostree/src/ostree/ot-main.h

Purpose: defines the shared command framework ABI for OSTree CLI builtins and admin builtins.

Important APIs/types/functions: `OstreeBuiltinFlags` controls repo opening/checking and hidden commands. `OstreeAdminBuiltinFlags` controls superuser checks, sysroot locking/loading, and sysroot omission. `OstreeCommand` names a command, flags it, provides its function pointer, and optional description. `OstreeCommandInvocation` currently wraps the selected command for extensibility. The header declares `ostree_main()`, `ostree_run()`, usage, external command lookup/exec, repo/sysroot parsers, admin parsers, `ostree_ensure_repo_writable()`, GPG result printing, and tombstone config enabling.

Control flow/state: this header supplies no implementation but defines how commands receive `argc/argv`, invocation metadata, cancellables, and `GError` propagation.

Dependencies/integration: includes `libglnx.h` and `ostree.h`. Remote, admin, and root builtins include this header directly or via subsystem builtin headers.

Risks: command flags are bitmasks; using the wrong flag can silently skip repo opening, skip repo checks, fail to lock sysroot, or demand unnecessary privileges. The terminal color helpers depend on `glnx_stdout_is_tty()`.

Test signals: broad compile coverage plus CLI integration tests. `admin-test.sh` is a strong signal for admin flags, sysroot loading, and `--print-current-dir`.
