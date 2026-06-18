# sources/distributed-fs/ceph-client/arch/s390/lib/uaccess.c

## Purpose
Implements s390 user-address-space compare-and-exchange helpers with storage-key handling, plus an optional debug assertion for user/kernel ASCE state.

## Important APIs, Types, And Functions
Under `CONFIG_DEBUG_ENTRY`, `debug_user_asce()` verifies control registers 1 and 7 match the expected user ASCE on kernel entry/exit. Exported cmpxchg helpers are `__cmpxchg_key1()`, `__cmpxchg_key2()`, `__cmpxchg_key4()`, `__cmpxchg_key8()`, and `__cmpxchg_key16()`. `__cmpxchg_key_small()` implements byte/halfword cmpxchg by aligning to a 32-bit word, masking, and retrying a word `cs`.

## Control Flow And State
All cmpxchg helpers initialize storage-key regions, switch access key with `spka`, execute the appropriate compare-and-swap instruction (`cs`, `csg`, `cdsg`), restore the default key, and use exception-table fixups to return errors and previous values on user access faults. Small sizes loop up to 128 times to handle concurrent modification of unrelated bytes in the containing word, returning `-EAGAIN` if retry budget is exhausted.

## Dependencies And Integration
Depends on uaccess, kprobes annotations, MM/storage-key helpers, control-register access, s390 exception-table macros, and exported architecture atomics used by futex/user-memory paths.

## Risks And Test Signals
Risks include failing to restore access key, exception-table mistakes, byte-order shift/mask errors, livelock or excessive `-EAGAIN`, and faults while in kprobe context. Signals include futex/atomic user access tests, storage-key tests, debug-entry panics, fault-injection on user pages, and KASAN remaining disabled by the Makefile.
