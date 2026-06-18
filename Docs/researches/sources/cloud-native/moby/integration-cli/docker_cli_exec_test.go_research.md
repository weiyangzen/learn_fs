# sources/cloud-native/moby/integration-cli/docker_cli_exec_test.go

Purpose: integration coverage for `docker exec` behavior across interactive I/O, environment propagation, exit status, paused containers, TTY/stdin handling, cgroups, exec inspect lifecycle, links, mutable network files, users, privileges, readonly containers, ulimits, startup failures, and Windows PATH preservation.

Important APIs/types/functions: `DockerCLIExecSuite`; `TestExec`, `TestExecInteractive`, `TestExecAfterContainerRestart`, daemon-suite `TestExecAfterDaemonRestart`, `TestExecEnv`, `TestExecSetEnv`, `TestExecExitStatus`, `TestExecPausedContainer`, `TestExecTTYCloseStdin`, `TestExecTTYWithoutStdin`, `TestExecParseError`, `TestExecStopNotHanging`, `TestExecCgroup`, `TestExecInspectID`, `TestLinksPingLinkedContainersOnRename`, `TestRunMutableNetworkFiles`, `TestExecWithUser`, `TestExecWithPrivileged`, `TestExecWithImageUser`, `TestExecOnReadonlyContainer`, `TestExecUlimits`, `TestExecStartFails`, and `TestExecWindowsPathNotWiped`.

Control flow: tests run sleeping/top containers, execute commands through CLI or `exec.Command`, use pipes for interactive stdin/stdout, inspect daemon fields, and sometimes call the Docker API for `ExecInspect`. Concurrency is used for cgroup consistency checks and stop-not-hanging behavior.

State and persistence: creates running containers, exec instances, environment variables, network files, cgroup state, user accounts inside images, device nodes under privileged exec, and inspectable exec IDs. It verifies exec records after completion and deletion after container removal.

Dependencies and integration points: Docker CLI, Docker API client, busybox shell tools, build helper, local daemon storage paths, platform gates for Linux/Windows, cgroups, user namespace constraints, and `icmd`.

Risks: interactive and TTY tests are timing-sensitive. Cgroup tests depend on cgroup layout and userns. Privileged exec tests require Linux capabilities. Network file mutation reads daemon storage directly and is local-daemon-only.

Test signals: failures show regressions in exec process lifecycle, environment merge rules, terminal handling, inspect persistence, cgroup placement, privilege scoping, readonly compatibility, ulimit inheritance, or platform-specific path handling.
