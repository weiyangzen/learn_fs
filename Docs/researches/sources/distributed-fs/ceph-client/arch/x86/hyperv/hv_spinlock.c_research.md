## `sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_spinlock.c`

Purpose: installs Hyper-V paravirtual queued spinlock waiting/kicking operations so vCPUs can enter a hypervisor idle state while spinning.

Important APIs and functions: `hv_init_spinlocks()` patches `pv_ops_lock`; `hv_qlock_wait()` waits via `HV_X64_MSR_GUEST_IDLE`; `hv_qlock_kick()` sends an IPI to wake a waiting CPU; `hv_vcpu_is_preempted()` is a stub returning false; `hv_parse_nopvspin()` handles `hv_nopvspin`.

Control flow: initialization requires the command-line feature not disabled, APIC availability, Hyper-V cluster IPI recommendation, and guest-idle MSR support. Wait disables interrupts, rechecks the lock byte against the expected value to avoid missed wakeups, reads the guest-idle MSR, and restores interrupts. Kick sends `X86_PLATFORM_IPI_VECTOR`.

State and persistence: `hv_pvspin` is boot-time state. Runtime state is in global paravirt lock ops; no private per-lock state is stored here.

Dependencies and integration points: paravirt queued spinlock core, APIC IPI send, Hyper-V feature/hint bits, and MSR access.

Risks: the race between unlock IPI and entering guest idle is the central hazard; interrupt disabling and lock-byte recheck are required. NMI context cannot safely idle and returns immediately.

Test signals: boot logs for enabled/disabled PV spinlocks, lock stress under Hyper-V, command-line `hv_nopvspin`, and no CPU offline or spinlock hang under contention.
