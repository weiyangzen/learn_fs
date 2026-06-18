# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_anti_rb.c

## Purpose
This file implements anti-rollback helpers for QAT firmware security version number (SVN) handling. It wraps admin SVN query/commit commands and checks hardware SVN status CSRs for pass/fail/retry/no-status outcomes.

## Important APIs, Types, And Functions
Public APIs are `adf_anti_rb_commit()`, `adf_anti_rb_query()`, and `adf_anti_rb_check()`. `adf_anti_rb_check()` uses `GET_ANTI_RB_DATA()` to access generation-specific anti-rollback offsets and enablement callbacks.

## Control Flow
Query and commit delegate to admin commands. `adf_anti_rb_check()` looks up the QAT device from a PCI device, skips if the generation does not enable anti-rollback, reads the configured SVN status CSR, extracts `ADF_SVN_STS_MASK`, and returns success, `-EIO`, `-EAGAIN`, `-ETIMEDOUT`, or `-EINVAL` depending on status and retry count.

## State And Persistence Behavior
State is volatile in `hw_device->anti_rb_data.svncheck_retry` and `sysfs_added` managed elsewhere. Retry count resets on pass or timeout.

## Dependencies And Integration Points
It depends on admin SVN commands, generation-specific anti-rollback metadata, PCI device manager lookup, CSR access to PMISC, and likely sysfs code outside this file.

## Risks
Retry behavior sleeps 250 ms per retry and permits 60 retries, so checks can span a significant time. Incorrect CSR offset or enablement predicate causes false pass/fail. Unknown status values return `-EINVAL`.

## Test Signals
SVN pass, fail, retry-to-pass, retry-timeout, and disabled-fuse scenarios; sysfs query/commit behavior; and Gen6 anti-rollback hardware with valid admin AE communication are useful signals.
