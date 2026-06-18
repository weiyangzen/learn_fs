## sources/cloud-native/containers-storage/pkg/idtools/utils_unix.go

Purpose: Unix command lookup and execution helpers for idtools.

Important APIs/types/functions: `resolveBinary` and `execCmd`.

Control flow: `resolveBinary` uses `exec.LookPath`, resolves symlinks, and only accepts a binary whose resolved basename matches the requested name. `execCmd` splits an argument string on spaces and runs the command with combined stdout/stderr output.

State and persistence: spawns external commands; no persistent mutation by itself.

Dependencies and integration points: used by getent fallback and user/group creation.

Risks: `strings.Split(args, " ")` cannot represent quoted arguments or embedded spaces. Symlink basename enforcement rejects wrapper symlinks with different final names.

Test signals: no selected direct tests.
