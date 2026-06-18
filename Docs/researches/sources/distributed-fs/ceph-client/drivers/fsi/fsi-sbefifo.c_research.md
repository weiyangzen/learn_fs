<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-sbefifo.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-sbefifo.c

## Purpose
`fsi-sbefifo.c` provides the Linux device interface to the POWER Self Boot Engine FIFO. It registers an FSI client for SBEFIFO engines, exposes a character device for userspace command/response transactions, exports in-kernel `sbefifo_submit()` and `sbefifo_parse_status()`, handles FIFO cleanup/reset, timeout reporting, SBE state checks, and FFDC collection.

## Important APIs, types, and functions
`struct sbefifo` stores magic, FSI device, cdev device, lock, broken/dead/async-FFDC/timeout flags, and active timeout settings. `struct sbefifo_user` stores per-file command staging and timeout overrides. Exported functions are `sbefifo_submit()` and `sbefifo_parse_status()`. Core hardware helpers include `sbefifo_check_sbe_state()`, `sbefifo_request_reset()`, `sbefifo_cleanup_hw()`, `sbefifo_wait()`, `sbefifo_send_command()`, `sbefifo_read_response()`, `sbefifo_do_command()`, and `__sbefifo_submit()`.

## Control flow
Probe allocates the SBEFIFO object, takes a reference on the FSI device, allocates a source-tree FSI minor, registers `sbefifoN`, creates OF platform children such as OCC, and exposes a read-only `timeout` attribute. Kernel clients call `sbefifo_submit()`, which builds a kernel iov iterator, locks the FIFO, validates command length, cleans hardware, optionally collects async FFDC, sends the command into the UP FIFO with EOT, reads DOWN FIFO words until EOT, resets on failures, and returns response word count. Userspace writes stage one command, except the magic `"RSET"` word triggers reset immediately; a later read executes the staged command into the user buffer. Ioctls adjust command and read timeouts per open file.

## State and persistence behavior
State is runtime-only. `broken` forces reset before reuse, `dead` rejects submissions during removal, `async_ffdc` tracks mailbox-reported asynchronous FFDC, and `timed_out` is exposed through sysfs with notifications. Per-open staged commands can be page-backed or vmalloc-backed and are released after read or close.

## Dependencies and integration points
It depends on the FSI device APIs, FSI cdev minor helpers, OF child platform creation, cdev/fs/uaccess/uio iterators, vmalloc, SBEFIFO UAPI ioctls, and SBE/OCC command constants. `fsi-occ.c` uses its exported submission/status parsing helpers.

## Risks and edge cases
FIFO reset and cleanup are central: parity errors, non-empty FIFOs, EOT acknowledgement failures, SBE reset requests, and timeouts all need to leave the next command safe. Response overflow returns `-EOVERFLOW` while still draining to EOT. `sbefifo_parse_status()` returns positive SBE primary status values distinct from Linux errors. Userspace depends on `-EAGAIN` when reading without a staged command. Concurrency is serialized by the device lock plus per-file locks.

## Test signals
Signals include probe/minor allocation, userspace write-then-read transactions, reset magic handling, ioctl timeout changes, kernel `sbefifo_submit()` response length accounting, status parsing with FFDC, async FFDC retrieval, FIFO parity/reset/timeout paths, response overflow, SBE state rejection, child OCC creation/removal, and dead-device rejection during remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-sbefifo.c -->
