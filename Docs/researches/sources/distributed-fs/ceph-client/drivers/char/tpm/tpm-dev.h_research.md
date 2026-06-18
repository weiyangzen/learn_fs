<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev.h -->
# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev.h

## Purpose
Declares shared TPM character-device per-file state and common file operation helpers.

## Important APIs, Types, And Functions
Defines `struct file_priv` with chip pointer, optional `struct tpm_space`, buffer mutex, user-read timer, timeout and async work, wait queue, response length, response flags, command-enqueued flag, and `data_buffer[TPM_BUFSIZE]`. Declares `tpm_common_open/read/write/poll/release()`.

## Control Flow
The structure supports both raw and resource-manager devices: open initializes it, write fills `data_buffer`, async or sync transmit updates response state, read drains response bytes, and release flushes outstanding work/timers.

## State And Persistence
State persists per file descriptor and is guarded by `buffer_mutex`. The optional `space` pointer selects whether TPM2 commands are virtualized.

## Dependencies And Integration Points
Included by `tpm-dev.c`, `tpm-dev-common.c`, and the TPM resource-manager device implementation. It depends on TPM core types, poll types, mutexes, timers, workqueues, and wait queues through included headers.

## Risks And Edge Cases
All fields participate in concurrency behavior; missing mutex coverage can race reads, writes, async completion, and timeout cleanup. The fixed `TPM_BUFSIZE` buffer bounds user command and response sizes.

## Test Signals
Compile raw and resource-manager file operations, run concurrent poll/read/write tests, and validate buffer-state transitions under async completion and timeout cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/tpm/tpm-dev.h -->
