# sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_linux.go

Purpose: detects Linux operating system display name and whether PID 1 appears containerized.

Important APIs, types, and functions: package variables `proc1Cgroup`, `etcOsRelease`, `altOsRelease`; functions `GetOperatingSystem` and `IsContainerized`.

Control flow: `GetOperatingSystem` opens `/etc/os-release`, falls back to `/usr/lib/os-release`, scans for `PRETTY_NAME=`, parses with shellwords, and defaults to `"Linux"` if absent. `IsContainerized` reads `/proc/1/cgroup` and returns true when any non-empty cgroup path does not end in `/` or `init.scope`.

State and persistence: reads host/container files only. Test code can override package variables.

Dependencies and integration points: depends on `bufio`, `bytes`, `fmt`, `os`, `strings`, and `go-shellwords`. Used by environment reporting logic in containers-storage consumers.

Risks and edge cases: cgroup v2 and systemd layouts can evolve; heuristic may misclassify. PRETTY_NAME with spaces must be quoted. Scanner ignores read errors until after loop? It does not check `scanner.Err`, so read errors after scanning are not reported.

Test signals: Linux OS tests cover valid/invalid PRETTY_NAME, fallback file, and containerized/non-containerized cgroup layouts.
