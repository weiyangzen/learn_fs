# sources/distributed-fs/ceph-client/drivers/char/mem.c

## Purpose
`mem.c` implements the classic memory major character devices, including `/dev/mem`, `/dev/null`, `/dev/zero`, `/dev/full`, optional `/dev/port`, and the registration hooks for `/dev/random`, `/dev/urandom`, and `/dev/kmsg`. It registers major `MEM_MAJOR`, creates class devices from `devlist[]`, and dispatches each opened minor to its specialized `file_operations`.

## Important APIs, Types, and Functions
- `devlist[]` maps minor numbers to names, fops, extra `fmode_t` bits, and default device-node modes. Minor `1` is `/dev/mem`, `3` is `/dev/null`, `4` is `/dev/port` when configured, `5` is `/dev/zero`, `7` is `/dev/full`, `8` and `9` are `random_fops` and `urandom_fops`.
- `memory_open()` validates the minor, replaces `filp->f_op` with the target operations, adds `FMODE_NOWAIT` where supported, and calls target `.open` if present.
- `/dev/mem` uses `read_mem()`, `write_mem()`, `mmap_mem_prepare()`, `memory_lseek()`, and `open_port()`.
- `/dev/zero` uses `read_zero()`, `read_iter_zero()`, shared/private mmap setup via `mmap_zero_prepare()`, and `get_unmapped_area_zero()`.
- `/dev/null` discards writes, returns EOF on reads, supports splice writes and `uring_cmd_null()`.
- `/dev/full` reads as zeroes but writes fail with `-ENOSPC`.
- `chr_dev_init()` registers the major, registers the `mem` class, creates device nodes, and finally calls `tty_init()`.

## Control Flow
Open first enters the generic `memory_fops.open`, then `memory_open()` selects an entry in `devlist[]`. `/dev/mem` reads and writes iterate page-sized physical-address spans, check architecture address validity, check `page_is_allowed()`, translate physical memory with `xlate_dev_mem_ptr()`, and copy through a bounce buffer for reads. `/dev/mem` mmap validation checks physical offset overflow, architecture range validity, private mapping support, `range_is_allowed()`, and `phys_mem_access_prot_allowed()` before installing a remap action.

`/dev/zero` read paths repeatedly clear user memory or zero an iov iterator with rescheduling and signal checks. Private zero mappings are marked anonymous after successful mmap; shared mappings are backed through shmem. `/dev/port` loops byte-by-byte over I/O port space up to 65536 ports.

## State and Persistence
The file has no persisted software state beyond registered devices and class state. `/dev/mem` and `/dev/port` expose persistent machine physical memory or I/O-port state directly. `open_port()` gates raw I/O access with `CAP_SYS_RAWIO` and lockdown, and for `/dev/mem` replaces `f_mapping` with `iomem_get_mapping()` so driver revocations can be coordinated.

## Dependencies and Integration Points
This file sits at the core device namespace level. It depends on architecture hooks for physical address validity, strict devmem filtering, noncached protections, `/dev/port` availability, no-MMU behavior, and IO remapping. It integrates with `random_fops`, `urandom_fops`, `kmsg_fops`, shmem, splice, io_uring, device classes, and the security lockdown framework.

## Risks
- `/dev/mem` and `/dev/port` are high-risk interfaces because they expose physical memory and raw I/O; correctness depends heavily on `CONFIG_STRICT_DEVMEM`, `range_is_allowed()`, capabilities, and lockdown.
- Arithmetic around physical offsets is carefully checked in mmap but remains architecture-sensitive.
- `/dev/zero` shared/private mmap behavior must preserve long-standing userspace ABI expectations.
- Partial progress semantics in copy loops intentionally return partial counts on signal or fault after progress.

## Test Signals
Useful tests include opening each expected minor, verifying node modes, checking `/dev/null`, `/dev/zero`, and `/dev/full` read/write semantics, exercising nonblocking zero iter reads, testing `/dev/mem` denial without `CAP_SYS_RAWIO`, and architecture-specific mmap tests for invalid ranges and strict devmem filtering. Boot logs should show no major registration failure, and `/dev/port` should only appear when `arch_has_dev_port()` permits it.
