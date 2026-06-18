
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ccs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ccs.h

## Purpose
Defines UAPI constants for the CCS static-priority scheduler policy. It gives userspace the scheduler policy number and priority range used when requesting this policy through scheduler syscalls.

## APIs, Control Flow, and State
The header defines `SCHED_CCS`, `SCHED_CCS_PRIO_MIN`, and `SCHED_CCS_PRIO_MAX`. There are no structures or functions. Runtime control flow is in scheduler policy validation and scheduling-class code that interprets these constants; per-task scheduling policy and priority are stored in kernel task state.

## Dependencies, Integration, Risks, and Tests
Integration points are `sched_setscheduler`/`sched_getscheduler`, scheduler policy tooling, and any CCS scheduling class implementation. Risks include policy-number collision, userspace using priorities outside the advertised range, and kernels without CCS support rejecting the policy. Test signals include scheduler syscall tests for min/max priority, invalid priority rejection, policy reporting, and runtime scheduling behavior under CCS-enabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ccs.h -->
