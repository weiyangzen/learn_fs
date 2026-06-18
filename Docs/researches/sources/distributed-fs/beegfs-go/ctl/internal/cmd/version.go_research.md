# sources/distributed-fs/beegfs-go/ctl/internal/cmd/version.go

Purpose: implements the `version` command for printing CTL build and protocol compatibility information.

Important APIs/types/functions: package variables `BinaryName`, `Version`, `Commit`, and `BuildTime`; package variable `versionCmd`.

Control flow: command accepts no args and prints version, commit, and build time. It also prints a hint that this is the command-line tool version. When global debug is enabled it prints effective and real UID/GID details.

State and persistence: read-only, no runtime state mutation.

Dependencies and integration points: integrates Cobra, Viper debug config, backend config key constants, and Unix identity syscalls.

Risks: if build variables are not set by linker flags, output contains defaults such as `local-build` and `unknown`. Version output is user/script-facing and should remain stable. Debug mode exposes process identity information.

Test signals: no direct tests. Useful tests would validate no-arg enforcement and that required version fields are present under default and injected build variables.
