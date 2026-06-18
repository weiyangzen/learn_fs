<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-audit.h -->
# sources/distributed-fs/ceph-client/drivers/md/dm-audit.h

## Purpose
`dm-audit.h` is the public DM audit wrapper interface, compiling to real audit calls with `CONFIG_DM_AUDIT` and no-op inline stubs otherwise.

## Important APIs, Types, And Functions
Enabled builds declare `dm_audit_log_bio()` and `dm_audit_log_ti()`, plus wrappers `dm_audit_log_ctr()`, `dm_audit_log_dtr()`, and `dm_audit_log_target()`. Disabled builds provide matching empty inline functions.

## Control Flow
DM targets call the wrapper for constructor, destructor, or target events. Enabled builds forward to `dm_audit_log_ti()` with `AUDIT_DM_CTRL` or `AUDIT_DM_EVENT`; disabled builds return immediately.

## State And Persistence
The header stores no state and only gates whether audit records can be emitted.

## Dependencies, Integration Points, Risks, And Test Signals
It includes Device Mapper and audit headers and is consumed by DM targets. Risks are audit coverage disappearing in disabled builds, caller prefix/result misuse, and signature drift with `dm-audit.c`. Test both configs and inspect target wrapper use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-audit.h -->
