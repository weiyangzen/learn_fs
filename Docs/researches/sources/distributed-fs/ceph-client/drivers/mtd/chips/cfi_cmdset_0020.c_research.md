## sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_cmdset_0020.c

Purpose: implements the MTD NOR command-set driver for CFI primary/alternate command set `0x0020`, the ST Advanced Architecture command set. It turns CFI geometry and ST extended-query data into an `mtd_info` device and provides read, buffered write, writev, erase, lock, unlock, sync, suspend, resume, and destroy callbacks.

Important APIs, types, and functions: `cfi_cmdset_0020()` is the exported command-set entry called by generic CFI probing. `cfi_staa_setup()` builds erase-region metadata and installs the MTD callbacks. `do_read_onechip()`, `do_write_buffer()`, `do_erase_oneblock()`, `do_lock_oneblock()`, and `do_unlock_oneblock()` are the per-chip state-machine operations. `cfi_staa_write_buffers()` enforces write-buffer boundaries, while `cfi_staa_writev()` coalesces vectored writes around the ECC-sized write unit.

Control flow: probe reads the ST PRI table with `cfi_read_pri()`, validates version 1.0 through 1.3, byteswaps feature masks, initializes each `flchip`, and calls setup. Runtime operations split requests by chip and erase-region boundaries, acquire each chip mutex, wait or sleep on the chip wait queue until the state is usable, issue ST/Intel-style command sequences through `map_write()`, poll status bit `0x80`, and wake waiters after state changes. Reads can suspend an in-progress erase when supported, copy data, then resume erase.

State and persistence: state is per-chip `flchip.state`, `oldstate`, wait queues, mutexes, adaptive write/erase timing fields, and hardware status/VPP state. MTD geometry persists in `mtd_info` erase regions and write-buffer size. Suspend marks idle chips `FL_PM_SUSPENDED`; resume sends reset/read-array and restores `FL_READY`.

Dependencies and integration points: depends on CFI/map helpers, `struct cfi_private`, `map_info` accessors, `ENABLE_VPP`/`DISABLE_VPP`, CFI geometry macros, and generic MTD callbacks. It is loaded indirectly by `gen_probe.c` when CFI reports `P_ID_ST_ADV`.

Risks: write-buffer alignment is strict and returns `-EINVAL` for unaligned starts. Long erase/lock/unlock paths use coarse sleeps and polling. `cfi_staa_unlock()` only calls one block helper despite taking a length, so range-unlock expectations need scrutiny. `writev()` has fragile partial-buffer accounting around `thislen`. Status handling merges interleaved-chip errors only in erase.

Test signals: successful CFI detection of ST advanced parts, correct erase-region layout, reads during erase suspend/resume, aligned and boundary-crossing buffered writes, `-EROFS` on locked blocks, suspend returning `-EAGAIN` during active operations, and no stuck `FL_*` states or waiters after timeout/error paths.
