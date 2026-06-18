# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_bitmap_gen.h

## Purpose

`ip_set_bitmap_gen.h` is a C template used by concrete bitmap set modules. A module defines `MTYPE` and type-specific callbacks, includes this header, and receives a complete `struct ip_set_type_variant` with add, delete, test, list, flush, destroy, head, garbage collection, and extension handling.

## Important APIs And Types

The header token-pastes names such as `mtype_add`, `mtype_del`, `mtype_test`, `mtype_list`, `mtype_gc`, and `mtype_variant`. It expects a concrete map type with `members`, `elements`, optional `extensions`, optional `gc`, and a `set` backpointer. Concrete modules provide `mtype_do_test`, `mtype_do_add`, `mtype_do_del`, `mtype_do_list`, `mtype_do_head`, `mtype_kadt`, `mtype_uadt`, and `mtype_same_set`. `IP_SET_BITMAP_STORED_TIMEOUT` enables special handling for set types that can store timeout values before an element is fully active.

## Control Flow

`mtype_add` checks whether the type-specific add reports an existing element, a re-add, or a stored-timeout transition, then initializes timeout, counter, comment, and skbinfo extensions before setting the membership bit and incrementing `set->elements`. `mtype_del` clears membership through the type callback, destroys extensions, decrements the element count, and treats an expired timeout as already absent.

`mtype_test` first checks the membership bit through the type callback, then uses `ip_set_match_extensions` to enforce timeout, counters, counter-match flags, and skbinfo output. `mtype_list` iterates member IDs from the netlink callback cursor, skips absent and expired entries, emits type-specific data, and appends extensions. `mtype_gc` is timer based: it locks the set, scans all possible IDs, clears expired entries, destroys extensions, and reschedules itself. `mtype_head` emits range metadata from the concrete type plus references, memory size, element count, and flags.

## State And Persistence

The bitmap state is in an in-memory bitset plus per-element extension storage. The template mutates `set->elements` and `set->ext_size`. Timeout GC is a kernel timer. There is no disk persistence; state is recreated from userspace commands or restore files.

## Dependencies And Integration

The template depends on `ip_set_core.c` exports for allocation, extension matching, extension serialization, timeout helpers, comments, counters, and flags. It is included by bitmap IP, bitmap IP/MAC, and bitmap port modules. It assumes callers hold the set lock for mutating ADT operations, which the core enforces for userspace and kernel add/delete paths.

## Risks

Because this is macro-generated code, each including module must satisfy the expected callback and data layout contract. Extension offsets are pointer arithmetic over flexible storage, so incorrect `set->dsize` or element alignment in a concrete module can corrupt state. Timeout handling differs when `IP_SET_BITMAP_STORED_TIMEOUT` is set, making partially filled elements a special risk. Listing must maintain the callback cursor correctly or netlink dumps can loop or omit entries.

## Test Signals

Test add/delete/test/list/flush/destroy with and without timeout, counters, comments, and skbinfo for every bitmap type. Exercise expired entries, re-add with `-exist`, list buffer exhaustion, and module unload after active timeout timers. KASAN and lockdep are useful for extension layout and timer lifetime bugs.
