# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/callb.c

FreeBSD implementation of Solaris `callb` callback registration used for CPR-style thread coordination.

Key behavior:
- Maintains a global `callb_table_t` with per-class callback lists and a freelist.
- `callb_add()` and `callb_add_thread()` register callbacks for current or specified threads.
- `callb_delete()` waits if the callback is executing, unlinks it, and returns its structure to the freelist.
- `callb_execute_class()` runs callbacks in a class serially and returns the registered name for the first failure.
- `callb_generic_cpr()` updates CPR event bits and optionally waits for safe state.
- `callb_lock_table()` and `callb_unlock_table()` stop/start new registrations.

`SYSINIT` and `SYSUNINIT` initialize and drain the callback system.
