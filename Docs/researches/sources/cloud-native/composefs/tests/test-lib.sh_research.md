# sources/cloud-native/composefs/tests/test-lib.sh

## Purpose
`test-lib.sh` provides common shell helpers and host capability probes for composefs tests.

## Important APIs, Types, And Functions
Helpers include `fatal`, `_fatal_print_file`, `assert_file_has_content`, `check_whiteout`, `check_fuse`, `check_erofs_fsck`, `check_fsverity`, and `assert_streq`. It initializes `can_whiteout`, `has_fuse`, `has_fsck`, and `has_fsverity`.

## Control Flow
On source, it defines helpers, runs probes unless variables already exist, and prints detected test options. Probes check `mknod`, FUSE tooling/capabilities, `fsck.erofs`, and fsverity enablement.

## State And Persistence
Creates temporary files for probes and deletes them. Exports shell variables in the caller context.

## Dependencies And Integration Points
Sourced by most shell tests. Depends on common Unix tools, `capsh`, `fusermount`, `/dev/fuse`, and `fsverity` when available.

## Risks
Capability detection is host-sensitive and can skip meaningful coverage. Probe output can affect test logs.

## Test Signals
It gates optional paths so tests can distinguish unsupported host features from composefs failures.
