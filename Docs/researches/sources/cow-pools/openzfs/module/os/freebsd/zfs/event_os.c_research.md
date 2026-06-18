# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/event_os.c

## Scope

Small FreeBSD kqueue helper for ZFS event code. It initializes a `knlist` protected by an `sx` lock.

## Main Interfaces

- `knlist_init_sx(struct knlist *knl, struct sx *lock)` installs lock, unlock, and assertion callbacks for a `knlist`.

## State And Control Flow

The helper callbacks call `sx_xlock()`, `sx_xunlock()`, and `sx_assert()` based on requested lock state. There is no persistent file-local state.

## Dependencies

Uses FreeBSD `struct knlist`, `struct sx`, and event/kqueue locking contracts.

## Correctness Notes

This allows FreeBSD event notification code to use `sx` locks where `knlist_init()` expects function pointers for locking and assertions.
