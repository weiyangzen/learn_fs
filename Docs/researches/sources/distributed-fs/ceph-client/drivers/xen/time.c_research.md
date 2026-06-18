# sources/distributed-fs/ceph-client/drivers/xen/time.c

## Purpose
`time.c` implements Xen runstate and stolen-time accounting. It registers per-VCPU runstate memory with Xen and supplies paravirtual steal-clock data to the Linux scheduler/accounting code.

## Important APIs, types, and functions
Important state is per-CPU `struct vcpu_runstate_info xen_runstate` and `old_runstate_time`. Public functions are `xen_manage_runstate_time`, `xen_vcpu_stolen`, `xen_steal_clock`, `xen_setup_runstate_info`, and `xen_time_setup_guest`. Helpers `get64` and `xen_get_runstate_snapshot_cpu_delta` take consistent hypervisor-updated snapshots.

## Control flow
Setup enables Xen's runstate update flag assist when possible, updates the paravirtual `pv_steal_clock` static call, and enables scheduler static keys. Each CPU registers its runstate memory via `VCPUOP_register_runstate_memory_area`. Steal-clock reads snapshot the current runstate, add accumulated pre-suspend times, and report runnable plus offline time. Suspend/resume handling backs up runstate counters before suspend and accumulates them after resume.

## State and persistence
State is per-CPU runtime memory shared with the hypervisor plus accumulated counters preserved across suspend/resume. It is not durable beyond boot. The snapshot code treats `state_entry_time` and `XEN_RUNSTATE_UPDATE` as synchronization markers.

## Dependencies and integration points
It depends on Xen vcpu and vm-assist hypercalls, paravirt steal-clock static calls, scheduler cputime accounting, static keys, and Xen event/feature definitions.

## Risks and test signals
Risks include inconsistent 64-bit reads on 32-bit kernels, missing memory barriers around hypervisor updates, suspend/resume counter duplication or loss, CPU hotplug registration failures, and differences when remote runstate updates are required. Test signals include stolen-time accounting in busy/oversubscribed guests, 32-bit PV guests, suspend/resume, CPU hotplug, scheduler stat validation, and hypervisor assist unavailable paths.
