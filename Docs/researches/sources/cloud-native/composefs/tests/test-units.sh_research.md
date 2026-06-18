# sources/cloud-native/composefs/tests/test-units.sh

## Purpose
`test-units.sh` is a shell unit suite for common tool/library behaviors: inline-vs-object storage, mount digest validation, and file measurement digest output.

## Important APIs, Types, And Functions
Functions are `makeimage`, `countobjects`, `test_inline`, `test_objects`, `test_mount_digest`, `test_composefs_info_measure_files`, and `test_composefs_info_help` (defined but not included in `TESTS`). It loops over `TESTS` and reports per-test status.

## Control Flow
The script creates a temp workdir, sources capability helpers, then for each named test creates root/objects/mnt dirs. Inline test expects no objects for a small file; object test expects one digest-store object for a 1024-byte file; mount digest test checks no-verity and wrong-verity failures then valid digest progress; measure-file test asserts known fs-verity-compatible digests.

## State And Persistence
Uses temporary directories under `/var/tmp` by default to improve fsverity support, and removes the workdir on exit. It may enable fsverity on temp files/images.

## Dependencies And Integration Points
Depends on built tools, `fsverity` when available, `mount.composefs`, and helpers from `test-lib.sh`.

## Risks
Mount assertions allow permission/sandbox errors after digest validation, so it proves pre-mount digest gating more than full mount success. `test_composefs_info_help` references `composefs_info` with an underscore and is not run.

## Test Signals
High-value targeted coverage for inline threshold behavior, digest store object creation, fsverity measurement compatibility, and mount digest error mapping.
