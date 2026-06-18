# sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/arcmsr_attr.c

## Purpose
`arcmsr_attr.c` exposes Areca adapter management and status through sysfs. It provides three privileged binary message-unit files (`mu_read`, `mu_write`, `mu_clear`) under the SCSI host device and a host attribute group with driver, firmware, queue, reset, and abort counters.

## Important APIs and functions
- `arcmsr_sysfs_iop_message_read()` drains bytes from `acb->rqbuffer` into the user buffer, refreshes from the firmware read queue when overflow was recorded, and requires `CAP_SYS_ADMIN`.
- `arcmsr_sysfs_iop_message_write()` accepts up to `ARCMSR_API_DATA_BUFLEN` bytes, stages them in `acb->wqbuffer`, and triggers `arcmsr_write_ioctldata2iop()` when firmware has cleared the previous write buffer.
- `arcmsr_sysfs_iop_message_clear()` clears firmware and driver management queues, resets ring indices, and marks management-buffer flags as cleared/read.
- `arcmsr_alloc_sysfs_attr()` creates `mu_read`, `mu_write`, and `mu_clear`, rolling back already-created files on failure.
- `arcmsr_free_sysfs_attr()` removes the three binary files during teardown.
- Attribute show callbacks expose `ARCMSR_DRIVER_VERSION`, `ccboutstandingcount`, `num_resets`, `num_aborts`, `firm_model`, `firm_version`, `firm_request_len`, `firm_numbers_queue`, `firm_sdram_size`, and `firm_hd_channels`.
- `arcmsr_host_groups` is consumed by the SCSI host template in `arcmsr_hba.c`.

## Control flow and state behavior
Management read uses `rqbuffer_lock`, computes circular-buffer occupancy with `CIRC_CNT`/`CIRC_CNT_TO_END`, copies up to `ARCMSR_API_DATA_BUFLEN`, advances `rqbuf_getIndex`, and then tries to pull more firmware data if `ACB_F_IOPDATA_OVERFLOW` had been set. Management write uses `wqbuffer_lock`; if there is already queued data, it nudges the IOP and returns `0` to ask user space to retry, otherwise it copies data into the circular write queue and posts to firmware when `ACB_F_MESSAGE_WQBUFFER_CLEARED` is set. Clear resets both driver rings and asks the firmware side to clear its read queue.

## Persistence behavior
The sysfs files are dynamic and exist only while the SCSI host is registered and `arcmsr_alloc_sysfs_attr()` succeeds. All message data is transient in adapter memory and driver ring buffers. The status attributes reflect live counters and firmware config captured by probe/config refresh; they do not write persistent state.

## Dependencies and integration points
This file depends on Linux sysfs binary attributes, SCSI host conversion (`class_to_shost`), capability checks, circular-buffer helpers, and the exported buffer helpers implemented in `arcmsr_hba.c`. It integrates with the SCSI host template through `arcmsr_host_groups` and with PCI probe/remove through explicit allocation/free helpers.

## Risks and edge cases
- The binary management channel is privileged but still copies raw firmware management data. Buffer length checks and ring bounds are critical.
- `mu_clear` only zeros `sizeof(struct QBUFFER)` bytes in each driver queue, not the full `ARCMSR_MAX_QBUFFER`; this matches existing code but is a notable partial-clear behavior.
- Write returns `0` when firmware is busy instead of a blocking wait, so user tools must retry.
- Correct behavior depends on `rqbuffer_lock`/`wqbuffer_lock` matching the interrupt handlers that fill and drain management queues.
- Overflow recovery re-enters firmware read-buffer handling while the read lock is held; regressions here could lose management data or keep `ACB_F_IOPDATA_OVERFLOW` set forever.

## Test signals
- `ls`/read of host sysfs attributes should show version, counters, firmware model/version, and firmware queue metadata.
- Non-admin access to `mu_read`, `mu_write`, and `mu_clear` should fail with `-EACCES`.
- Large writes above `ARCMSR_API_DATA_BUFLEN` should fail with `-EINVAL`.
- Management utility tests should verify ring wraparound, retry-on-busy write behavior, clear behavior, and overflow recovery after firmware posts more data than local free space.
