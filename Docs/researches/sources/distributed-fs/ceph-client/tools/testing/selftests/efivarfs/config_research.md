# sources/distributed-fs/ceph-client/tools/testing/selftests/efivarfs/config

## Purpose
Kernel config fragment for efivarfs selftests.

## Important APIs, Types, And Functions
Sets `CONFIG_EFIVAR_FS=y`.

## Control Flow
Consumed by selftest config tooling.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Required for mounting efivarfs at `/sys/firmware/efi/efivars`.

## Risks
EFI firmware availability and efivarfs mount state remain runtime prerequisites outside this fragment.

## Test Signals
Runtime shell test checks root privileges and an efivarfs mount as practical config signals.
