## sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_windows.go

**Purpose:** Implements Windows-specific WORKDIR normalization and command-line resolution for classic builds, including LCOW behavior.

**Important APIs:** `normalizeWorkdir`, `normalizeWorkdirUnix`, `normalizeWorkdirWindows`, and `resolveCmdLine`. A lazy regexp detects invalid `C:.` drive-current-directory forms.

**Control flow:** `normalizeWorkdir` dispatches to Windows or Unix normalization based on target platform. Windows normalization cleans current/requested paths, rejects drive-current-directory forms, converts relative or separator-rooted paths to `C:\...`, joins with current when appropriate, and uppercases drive letters. `resolveCmdLine` returns single escaped shell-form strings for WCOW and normal argv arrays for exec form or LCOW.

**State and persistence:** Affects persisted image `WorkingDir`, `Cmd`, `Entrypoint`, `ArgsEscaped`, and cache keys.

**Dependencies and integration:** Used by dispatchers on Windows daemon builds. It integrates with container runtime expectations around HCS command-line escaping.

**Risks:** Windows shell-form handling intentionally uses original Dockerfile text, not parsed args, to preserve `cmd.exe` behavior. Small changes can break compatibility. Drive/path normalization is security- and UX-sensitive.

**Test signals:** `dispatchers_windows_test.go` covers workdir normalization. Dispatcher tests also validate warnings around mixed shell/exec forms.
