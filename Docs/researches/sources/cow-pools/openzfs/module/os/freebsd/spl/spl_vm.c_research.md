# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_vm.c

## Scope

Small VM compatibility shim exposing FreeBSD VM pager constants and object lock wrappers under ZFS/SPL names.

## Main Interfaces

- Exports constant aliases for `VM_PAGER_BAD`, `VM_PAGER_ERROR`, `VM_PAGER_OK`, `VM_PAGER_PEND`, `VM_PAGER_PUT_SYNC`, and `VM_PAGER_PUT_INVAL`.
- Provides `zfs_vmobject_assert_wlocked()`, `zfs_vmobject_wlock()`, and `zfs_vmobject_wunlock()`.

## Dependencies

Depends directly on FreeBSD VM headers and lock macros: `VM_OBJECT_ASSERT_WLOCKED`, `VM_OBJECT_WLOCK`, and `VM_OBJECT_WUNLOCK`.

## Correctness Notes

This file intentionally keeps the wrappers as hard functions for compatibility, even though assertion file/line reporting is less helpful than a macro would be. It has no internal state.
