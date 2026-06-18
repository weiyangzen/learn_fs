# sources/cloud-native/moby/integration/container/exec_test.go

Purpose: Cross-platform exec API coverage for stdin EOF handling, working directory and environment propagation, exec resize validation, user/group resolution, and additional group preservation.

Important APIs and flow: Tests use `ExecCreate`, `ExecAttach`, `ExecInspect`, `ExecStart`, `ExecResize`, raw `POST /exec/<id>/resize`, and helper `container.Exec`. `TestExecWithCloseStdin` attaches to `cat`, calls `CloseWrite`, and waits for output. `TestExec` verifies exec-specific `WorkingDir` and env. `TestExecResize` covers success, raw query validation errors, unknown exec ID, and stopped-container conflict. `TestExecUser` builds images missing `/etc/group` or `/etc/passwd` and checks user parsing errors or `id` output. `TestExecWithGroupAdd` verifies group-add survives exec with a configured user.

State and dependencies: Builds temporary busybox variants, runs containers with TTY/user/group settings, and exercises raw HTTP to bypass client-side validation.

Risks and signals: The file guards attach stream lifetimes, API validation, identity lookup compatibility, and runtime exec setup. Failures can cause hangs, broken terminal resizing, or privilege/user mapping regressions.
