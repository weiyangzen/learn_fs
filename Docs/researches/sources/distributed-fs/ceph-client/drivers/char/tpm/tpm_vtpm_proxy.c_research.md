# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_vtpm_proxy.c

## Purpose
Implements `/dev/vtpmx`, a factory for virtual TPM proxy devices where a userspace process emulates TPM hardware through an anonymous server-side file descriptor while clients use normal `/dev/tpm*` nodes.

## Important APIs, Types, And Functions
`struct proxy_dev` stores chip, flags, waitqueue, buffer mutex, state flags, request/response lengths, shared buffer, and registration work. Server-side file ops are `vtpm_proxy_fops_read()`, `vtpm_proxy_fops_write()`, `vtpm_proxy_fops_poll()`, and release. TPM callbacks are `vtpm_proxy_tpm_op_send()`, `vtpm_proxy_tpm_op_recv()`, `vtpm_proxy_tpm_op_status()`, `vtpm_proxy_tpm_req_canceled()`, and `vtpm_proxy_request_locality()`. Control path is `vtpmx_ioc_new_dev()`.

## Control Flow
Module init creates a workqueue and registers misc device `vtpmx`. A privileged `VTPM_PROXY_IOC_NEW_DEV` allocates proxy state and TPM chip, creates an anonymous server file, marks it opened, sets TPM2 flag if requested, queues TPM chip registration work, and returns fd/major/minor/tpm number to userspace. TPM core send copies a request into the proxy buffer and wakes the server. Server read blocks until request is available, copies it out, and marks waiting-for-response. Server write copies a response back, clears wait state, and wakes TPM core. Device release stops registration work, unregisters the chip if needed, and frees state.

## State And Persistence
State is in-memory per proxy device: open/registered/wait-response/driver-command flags, request/response buffer, and work item. No persistent TPM data is stored by the driver; userspace emulator owns persistence.

## Dependencies And Integration Points
Uses miscdevice, anon inode files, waitqueues, TPM core registration, TPM locality commands, user ABI `linux/vtpm_proxy.h`, and CAP_SYS_ADMIN for device creation.

## Risks And Edge Cases
The server fd lifetime controls device lifetime. Locality-setting commands are blocked from clients unless issued by the driver command path. Close races with chip registration are handled by work flushing and open-state wakeups. Buffer state is protected by mutex, but status reads check `resp_len` without locking. Userspace protocol errors surface as TPM command timeouts or `-EIO`.

## Test Signals
`VTPM_PROXY_IOC_NEW_DEV` permission and ABI fields, TPM1/TPM2 mode, request/response round trips, poll readiness, server close while client waits, close during registration work, locality command filtering, malformed response sizes, and module unload.
