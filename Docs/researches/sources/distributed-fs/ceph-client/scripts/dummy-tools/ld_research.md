# sources/distributed-fs/ceph-client/scripts/dummy-tools/ld

Purpose: Dummy linker shim that succeeds for Kconfig/build capability probes and reports a GNU-like version when asked.

Important APIs/functions: `arg_contain()` scans arguments. `--version` or `-v` prints `GNU ld (scripts/dummy-tools/ld) 2.50`.

Control flow: Handles version probes, otherwise exits successfully with no output.

State/persistence: Stateless.

Dependencies/integration: Used through `CROSS_COMPILE=scripts/dummy-tools/` for linker feature/version tests.

Risks: It does not link anything, so any workflow that proceeds to real build actions with dummy tools will produce false success or missing outputs.

Test signals: Verify `scripts/dummy-tools/ld --version`, `-v`, and arbitrary unsupported options all exit as Kconfig expects.
