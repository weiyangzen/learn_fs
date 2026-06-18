
# sources/distributed-fs/openafs/src/uss/uss_common.c

Purpose: `uss_common.c` owns the global working state shared by all `uss` modules and provides initialization/reset plus bounded field parsing for bulk files and ACL/template argument strings.

Important APIs and state: it defines exported buffers such as `uss_User`, `uss_Uid`, `uss_Server`, `uss_Partition`, `uss_MountPoint`, `uss_RealName`, `uss_Pwd`, `uss_Volume`, `uss_Cell`, and `uss_ConfDir`; flags such as `uss_DryRun`, `uss_SkipKaserver`, `uss_Overwrite`, `uss_SaveVolume`, `uss_ignoreFlag`, and `uss_syntax_err`; numeric IDs for volume/server/partition and desired UID; directory-pool storage; and the `uss_currentDir` cleanup stack. `uss_common_Init()` sets one-time defaults, including config directory and template line number. `uss_common_Reset()` clears per-account fields back to idle or saved values. `uss_common_FieldCp()` copies a delimited field with overflow detection.

Control flow: main calls `uss_common_Init()` once. Each single command and each bulk record calls `uss_common_Reset()` before filling account-specific fields. Field parsing consumes until separator, NUL, or newline, null-terminates the destination, skips excess input on overflow, and collapses repeated spaces when the separator is a space.

State and persistence: all storage is process-global and non-reentrant. It persists only for the process lifetime, but its values drive persistent side effects in other modules. Saved password path/format/restore/save-volume fields are intended to persist across resets.

Dependencies and integration: includes OpenAFS configuration constants and KAS name lengths. `line` is external parser state from the yacc/lex layer.

Risks: globals make concurrency impossible and make partial resets a source of cross-record leakage. Some arrays have strict legacy limits, especially eight-character usernames and sixteen-character passwords. `uss_common_Init()` never sets `initDone = 1`, so its guard is ineffective and repeated calls reinitialize defaults. Test signals should verify reset isolation between bulk lines, field overflow behavior, space-collapsing semantics, saved/default values, and repeated initialization.
