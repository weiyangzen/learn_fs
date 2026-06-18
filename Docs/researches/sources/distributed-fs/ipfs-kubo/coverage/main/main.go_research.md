# sources/distributed-fs/ipfs-kubo/coverage/main/main.go

Purpose: coverage-only wrapper binary used when collecting sharness coverage. Important API is `main`, built only with `testrunmain`.

Control flow: reads `IPFS_COVER_DIR`, creates a coverage profile temp file and return-code temp file, executes `ipfs-test-cover` with `-test.run ^TestRunMain$`, coverprofile path, and original CLI args after `--`, forwards stdio/env, sets Linux parent-death signal, forwards SIGHUP/SIGINT/SIGTERM to the child after start, waits for the child, reads the return code file, strips the trailing byte, parses an integer, and exits with that status.

State and persistence: writes temporary coverage and return-code files; coverage dir comes from make. No repo datastore state.

Dependencies/integration: os/exec, signal/syscall, `ipfs-test-cover`, and the `Rules.mk` coverage target.

Risks: assumes return file has at least one byte and a trailing delimiter; signal-forwarding goroutine blocks on signal channel forever until process exit; `Pdeathsig` is Unix-specific. Test signal is build-tagged coverage CI behavior rather than direct unit tests.
