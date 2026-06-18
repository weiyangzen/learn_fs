# sources/distributed-fs/ceph-client/io_uring/filetable.h

## Purpose
The header declares fixed-file table operations and defines inline helpers for bitmap and encoded file-slot state.

## Important APIs, Types, And Functions
- Public operations: allocate/free tables, install/remove fixed fd, and register allocation range.
- `io_file_bitmap_set()` and `io_file_bitmap_clear()` update bitmap and allocation hint with sanity warnings.
- `FFS_NOWAIT`, `FFS_ISREG`, and `FFS_MASK` encode request flags into low bits of `node->file_ptr`.
- `io_slot_flags()`, `io_slot_file()`, and `io_fixed_file_set()` decode/encode file pointers and flags.
- `io_file_table_set_alloc_range()` updates automatic allocation bounds and hint.

## Control Flow
Inline helpers provide fast bitmap and slot decoding paths used by request file lookup and registration.

## State And Persistence
The encoded `file_ptr` in resource nodes persists for the lifetime of registered slots. Allocation hint state persists per table.

## Dependencies And Integration Points
It depends on `io_uring_types.h`, resource node definitions, and `io_file_get_flags()` provided elsewhere. It is shared by fixed-file lookup, registration, fdinfo, and filetable implementation.

## Risks And Edge Cases
Pointer low-bit encoding assumes alignment leaves flag bits free. WARNs catch bitmap inconsistency but do not recover. Any change to request flag bit positions affects `io_slot_flags()` shifting.

## Test Signals
Fixed-file registration, NOWAIT flag behavior, fdinfo file printing, and KASAN/lockdep runs validate this header’s assumptions.
