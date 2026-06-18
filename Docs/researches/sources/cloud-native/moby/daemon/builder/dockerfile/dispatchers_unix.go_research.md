## sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_unix.go

**Purpose:** Provides Unix-specific WORKDIR normalization and command-line resolution.

**Important APIs:** `normalizeWorkdir` rejects empty requests, converts slashes, resolves relative paths under current workdir, and cleans absolute paths. `resolveCmdLine` prepends the configured shell for shell-form commands and always returns `argsEscaped=false`.

**Control flow:** Simple path branch on absolute vs relative; shell prepending depends on `ShellDependantCmdLine.PrependShell`.

**State and persistence:** No direct persistence, but output becomes image `WorkingDir`, `Cmd`, `Entrypoint`, and cache command data.

**Dependencies and integration:** Used by `dispatchWorkdir`, `dispatchRun`, `dispatchCmd`, and `dispatchEntrypoint`.

**Risks:** Path cleaning must preserve Docker compatibility for relative workdirs. Command resolution must match legacy shell-form behavior.

**Test signals:** `dispatchers_unix_test.go` covers workdir normalization cases.
