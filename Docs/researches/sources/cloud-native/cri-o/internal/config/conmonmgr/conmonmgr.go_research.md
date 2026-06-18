# sources/cloud-native/cri-o/internal/config/conmonmgr/conmonmgr.go

Purpose: probes the configured `conmon` binary and records feature support gates derived from its semantic version and help output. CRI-O uses this to decide whether it can pass newer conmon options.

Important APIs/types/functions: `ConmonManager` stores `conmonVersion`, `supportsSync`, and `supportsLogGlobalSizeMax`. `New(conmonPath)` validates an absolute path, runs `conmon --version`, parses the third field as semver, and initializes feature booleans. `parseConmonVersion`, `initializeSupportsLogGlobalSizeMax`, `SupportsLogGlobalSizeMax`, `initializeSupportsSync`, and `SupportsSync` are the core helpers.

Control flow: `New` fails early for relative paths, failed command execution, short version output, or invalid semver. Sync support is pure version comparison against `2.0.19`. Log global size support is true at `2.1.2` or higher, otherwise it falls back to `conmon --help` and checks for `--log-global-size-max`, allowing backports.

State and persistence behavior: state is process-local inside the manager. It shells out through `cmdrunner` but writes no files. Feature detection logs informational messages through logrus.

Dependencies/integration points: depends on `github.com/blang/semver/v4`, logrus, and CRI-O `utils/cmdrunner`. It integrates with runtime/conmon launch configuration by exposing feature predicates to callers.

Risks: version parsing assumes `conmon --version` has at least three fields and the version is field 3. A nonstandard backported build can still be detected for only `--log-global-size-max`, not `--sync`. Help-output probing is best-effort and silent on command failure.

Test signals: companion tests mock `cmdrunner` to cover path validation, command failure, short output, version parsing, semver threshold boundaries, and help-output backport detection.
