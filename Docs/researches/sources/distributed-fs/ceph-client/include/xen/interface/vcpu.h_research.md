# sources/distributed-fs/ceph-client/include/xen/interface/vcpu.h

## Purpose
`vcpu.h` defines Xen VCPU hypercall operations for VCPU initialization, hotplug, runstate and time accounting, periodic/single-shot timers, per-VCPU info placement, NMI delivery, and physical CPU identity lookup.

## Important APIs, Types, and Functions
Commands include `VCPUOP_initialise`, `up`, `down`, `is_up`, `get_runstate_info`, `register_runstate_memory_area`, timer set/stop operations, `register_vcpu_info`, `send_nmi`, `get_physid`, and `register_vcpu_time_memory_area`. Key structs include `vcpu_runstate_info`, `vcpu_register_runstate_memory_area`, `vcpu_set_periodic_timer`, `vcpu_set_singleshot_timer`, `vcpu_register_vcpu_info`, `vcpu_get_physid`, and `vcpu_register_time_memory_area`.

## Control Flow
The guest initializes VCPUs with architecture context, brings them up, and may later bring them down asynchronously. Runtime code can query or register shared runstate/time areas so Xen updates accounting without hypercalls. Timer operations arm per-VCPU timers, and privileged paths may send NMIs or query physical IDs.

## State and Persistence Behavior
State lives in Xen's VCPU records and in guest-provided shared memory areas. Runstate time accumulates across scheduling transitions, timer settings persist until stopped or fired, and registered `vcpu_info` placement remains active for the VCPU.

## Dependencies and Integration Points
This header is included by Linux Xen CPU hotplug, scheduler accounting, pvclock, event-channel, and suspend/resume code. It depends on Xen base time and VCPU info structures.

## Risks and Test Signals
Risks include registering memory that crosses page boundaries, interpreting asynchronous `VCPUOP_down` as complete too early, stale runstate update flags, timer deadlines in the past, and architecture-specific physical ID assumptions. Test signals include CPU hotplug, stolen-time accounting, vDSO/pvclock time reads, timer interrupt delivery, and NMI/physid privilege checks.
