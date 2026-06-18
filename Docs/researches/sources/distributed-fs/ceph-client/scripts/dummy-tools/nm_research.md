# sources/distributed-fs/ceph-client/scripts/dummy-tools/nm

Purpose: Dummy `nm` shim for build/Kconfig probes.

Important APIs/functions: Same `arg_contain()` pattern as dummy `ld`; version probes print `GNU nm (scripts/dummy-tools/nm) 2.50`.

Control flow: Emits GNU-like version only for `--version` or `-v`; all other invocations succeed silently.

State/persistence: Stateless.

Dependencies/integration: Part of the dummy cross-toolchain prefix used to expose broad configuration options.

Risks: Produces no symbol table output, so it only suits probes that inspect exit status or version.

Test signals: Version and silent-success probe invocations.
