# sources/cloud-native/containers-storage/pkg/mount/flags.go

Purpose: translates fstab-style mount option strings into platform mount flags and filesystem-specific data.

Important APIs, types, and functions: maps `flags`, `validFlags`, `propagationFlags`; functions `MergeTmpfsOptions`, `ParseOptions`, and `ParseTmpfsOptions`.

Control flow: `ParseOptions` splits comma options, sets or clears known flags, and passes unknown/unsupported options through as data. `ParseTmpfsOptions` validates data keys against tmpfs allowed keys. `MergeTmpfsOptions` walks options in reverse so later options win, removes defaults and duplicates, collapses mutually exclusive flag/data settings, and returns an error for invalid tmpfs keys.

State and persistence: no persistence. State is static option metadata and returned flag/data values.

Dependencies and integration points: depends on `fmt` and `strings`; constants come from OS-specific flag files. Used by `Mount`, `ForceMount`, tmpfs callers, and mount tests.

Risks and edge cases: unsupported platform constants are zero, so known but zero-valued options become data rather than flags. `ParseOptions` does not validate generic unknown data. Propagation flags collide under key `-1`, so only the latest propagation option survives in tmpfs merge.

Test signals: `mount_unix_test.go` checks basic parsing and tmpfs option merging/error behavior.
