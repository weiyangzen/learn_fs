# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_vm.c

## Purpose

`osi_vm.c` supplies UKERNEL stubs for VM and page-cache hooks required by shared OpenAFS code. In user-space libuafs there is no kernel VM cache to flush, truncate, or smush.

## Important APIs, Types, and Functions

The file defines `osi_VM_Truncate`, `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, and `osi_VM_FlushPages`. All are no-ops except `osi_VM_FlushVCache`, which returns success.

## Control Flow

There is no substantive control flow. Calls return immediately.

## State and Persistence Behavior

No state is read or written. File data persistence is handled through dcache and cache-file paths, not kernel VM pages.

## Dependencies and Integration Points

The functions satisfy the OSI VM hook contract used by generic OpenAFS vnode and cache code. They include UKERNEL and stats headers for compatibility.

## Risks and Edge Cases

Shared code that assumes VM hooks flush dirty memory must not rely on these stubs in UKERNEL. Data consistency must be covered by `afs_StoreAllSegments`, dcache writes, and explicit file operation paths.

## Test Signals

Build coverage is the main signal. Runtime tests should verify truncation, writeback, close, and fsync behavior through libuafs operations rather than these no-op hooks.
