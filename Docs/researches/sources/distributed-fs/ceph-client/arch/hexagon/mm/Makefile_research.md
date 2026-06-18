# sources/distributed-fs/ceph-client/arch/hexagon/mm/Makefile

## Purpose

`Makefile` selects Hexagon MM implementation objects for initialization, uaccess, faults, cache management, user-copy assembly, and TLB flushing. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The build API is the `obj-y` list for `init.o`, `uaccess.o`, `vm_fault.o`, `cache.o`, `copy_to_user.o`, `copy_from_user.o`, and `vm_tlb.o`. Concrete declarations observed in the file: Build/script rules: `obj-y := init.o uaccess.o vm_fault.o cache.o`, `obj-y += copy_to_user.o copy_from_user.o vm_tlb.o`.

## Control Flow, State, And Persistence

Build-time only; these objects become the architecture MM support library.

## Dependencies And Integration Points

It integrates with the Hexagon kernel Makefile and generic MM hooks.

## Risks And Test Signals

Risks are missing mandatory MM objects. Test signals are Hexagon link and boot into userspace.
 A local static signal for this file is that it has 8 lines and 191 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
