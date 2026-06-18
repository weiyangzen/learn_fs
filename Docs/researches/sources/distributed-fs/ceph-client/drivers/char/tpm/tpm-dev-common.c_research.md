<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev-common.c -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev-common.c

## Purpose
Implements the shared file operations behind `/dev/tpm*` and `/dev/tpmrm*`: command write, response read, polling, asynchronous nonblocking execution, timeouts, and TPM2 space preparation/commit.

## Important APIs, Types, And Functions
Key functions are `tpm_dev_transmit()`, `tpm_dev_async_work()`, `user_reader_timeout()`, `tpm_timeout_work()`, `tpm_common_open()`, `tpm_common_read()`, `tpm_common_write()`, `tpm_common_poll()`, `tpm_common_release()`, `tpm_dev_common_init()`, and `tpm_dev_common_exit()`. It uses `struct file_priv`, `tpm_dev_wq`, timers, workqueues, wait queues, and TPM2 space helpers.

## Control Flow
Write validates command size and embedded TPM length, ensures previous response was consumed or timed out, copies user data, and either queues async work for nonblocking files or synchronously takes chip ops and transmits. `tpm_dev_transmit()` ends any active TPM2 auth session, prepares the resource-manager space, transmits, commits or flushes the space, and synthesizes a TPM2 command-code response for unsupported commands. Read returns pending response bytes, zeroes consumed data, updates offsets, and clears the user-read timer when done.

## State And Persistence
Per-open `file_priv` persists the chip, optional TPM2 space, buffer, response length, read state, command-enqueued flag, timer, work items, and wait queue. Async results persist until userspace reads them or the 120-second timer clears the buffer.

## Dependencies And Integration Points
Used by `tpm-dev.c` and TPM resource-manager fops. It integrates `tpm_try_get_ops()`, `tpm_transmit()`, TPM2 space virtualization, Linux usercopy, poll, timers, and workqueues.

## Risks And Edge Cases
The write/read state machine must prevent overlapping commands and stale responses. Nonblocking errors are reported on the subsequent read. The timeout path is deprecated but still mutates response state. TPM2 space errors must flush loaded handles to avoid leaks.

## Test Signals
Blocking and nonblocking command tests, partial reads, write while response pending, user-read timeout, invalid embedded lengths, oversize writes, unsupported TPM2 command synthesis, resource-manager handle virtualization, and unregister while file descriptors are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev-common.c -->
