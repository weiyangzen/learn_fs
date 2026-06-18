# sources/distributed-fs/ceph-client/arch/s390/kernel/machine_kexec.c

Purpose: executes normal kexec and crash kdump transitions on s390, including system reset, purgatory checksum checks, status save, crashkernel protection, and relocation-code handoff.

Important APIs and state: implements `machine_kexec_prepare()`, `machine_kexec_cleanup()`, `machine_shutdown()`, `machine_crash_shutdown()`, `machine_kexec()`, crash resource protect/unprotect, and `crash_free_reserved_phys_range()`. It uses external `relocate_kernel` code and calls purgatory entry points via `call_nodat()`.

Control flow: normal kexec copies relocation code into the control code page, disables tracing/locks, stops CPUs, resets the system, and calls the relocation stub with the image list, entry, and DIAG 308 reset flags. Crash kexec validates purgatory checksum, logs LGR info, stores other CPU statuses, saves boot CPU vector/guarded-storage state, then tail-calls through `store_status()` into `__do_machine_kdump()`, which resets and calls purgatory.

Dependencies and integration: tied to kexec core, crash dump resources, lowcore, guarded storage, vector registers, pfault/CIO/SCLP reset, OS info reipl block preservation, SMP IPL CPU calls, and memory attribute helpers for crashkernel protection.

Risks and test signals: non-returning reset paths, crash CPU status consistency, purgatory checksum failures, and crashkernel memory permissions are high risk. Test normal kexec, kdump under load, crashkernel protect/unprotect, reserved range freeing, VM `diag10_range()`, and dump analysis backchains.
