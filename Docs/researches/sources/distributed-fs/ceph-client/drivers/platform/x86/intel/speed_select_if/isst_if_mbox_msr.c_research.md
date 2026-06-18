# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_if_mbox_msr.c

## Purpose

This backend implements Intel Speed Select mailbox commands through OS mailbox MSRs on Skylake-X style platforms.

## Important APIs, Types, And Functions

`isst_if_send_mbox_cmd()` performs the two-MSR mailbox transaction using `MSR_OS_MAILBOX_INTERFACE` and `MSR_OS_MAILBOX_DATA`. `msrl_update_func()` runs the transaction on the target CPU. `isst_if_mbox_proc_cmd()` validates commands, enforces CAP_SYS_ADMIN for set requests, dispatches with `smp_call_function_single()`, stores set commands for resume, and returns response data. A PM notifier calls `isst_resume_common()` after suspend/hibernate/restore.

## Control Flow

Module init matches `INTEL_SKYLAKE_X`, verifies mailbox MSRs, registers a MBOX callback with the common interface, and installs a PM notifier. User mailbox ioctls enter common code, then this backend executes on the requested logical CPU to avoid cross-CPU MSR races.

## State And Persistence

The backend stores no per-device state. Resume persistence is delegated to the common replay hash. Firmware mailbox state is transient.

## Dependencies And Integration Points

It depends on x86 MSR access, CPU model matching, suspend notifiers, common ISST validation/storage helpers, and the `/dev/isst_interface` callback path.

## Risks

The retry count is intentionally small because MSR overhead is expected to cover firmware latency; slow firmware can return `-EBUSY`. Commands are executed on user-selected CPUs, so CPU hotplug and invalid logical IDs must be validated by common helper logic. All mailbox failures with low response byte set are collapsed to `-ENXIO`.

## Test Signals

MSR presence checks, invalid command rejection, set-request privilege checks, response-data reads, resume replay, CPU offline/online behavior, and busy-bit timeout handling are important signals.
