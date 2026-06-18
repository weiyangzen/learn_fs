# sources/cloud-native/moby/pkg/process/process_linux.go

Purpose: Linux-only zombie process detection.

APIs and flow: `zombie(pid)` rejects non-positive PIDs, reads `/proc/<pid>/stat`, splits the first fields, and returns true when the third column is `Z`. Missing proc entries are treated as non-zombie rather than errors.

State and dependencies: reads procfs on demand; no cached or persisted state. Uses `os.ReadFile`, `fmt`, and `bytes.SplitN`.

Integration points: exported Unix `Zombie` delegates here on Linux.

Risks and tests: procfs format parsing is intentionally minimal. Transient process exit can return false. No direct zombie fixture test exists in the listed file set.
