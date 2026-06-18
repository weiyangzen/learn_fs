# sources/distributed-fs/ceph-client/include/xen/interface/xenpmu.h

## Purpose
`xenpmu.h` defines Xen PMU virtualization operations, version fields, profiling modes/features, operation parameters, and the shared PMU interrupt data structure.

## Important APIs, Types, and Functions
Commands include `XENPMU_mode_get`, `mode_set`, `feature_get`, `feature_set`, `init`, `finish`, `lvtpc_set`, and `flush`. `struct xen_pmu_params` carries version, value, and target VCPU. Modes include `XENPMU_MODE_OFF`, `SELF`, `HV`, and `ALL`; `XENPMU_FEATURE_INTEL_BTS` describes BTS support. `struct xen_pmu_data` stores interrupted VCPU, physical CPU, domain ID, padding, and architecture-specific PMU data.

## Control Flow
Guests or dom0 call `HYPERVISOR_xenpmu_op` to query/set mode and features, initialize shared PMU handling, update LVTPC state, flush PMU state, and finish profiling. On PMU interrupts, Xen fills shared data and notifies the appropriate VCPU.

## State and Persistence Behavior
Mode and feature settings live in Xen PMU virtualization state. `xen_pmu_data` is shared live interrupt state written by Xen and read by the guest; architecture-specific fields may be bidirectionally writable depending on arch rules.

## Dependencies and Integration Points
It includes `xen.h` and relies on `struct xen_pmu_arch` from architecture headers. It integrates with Linux perf/Xen PMU support, VIRQ_XENPMU delivery, dom0 hypervisor profiling, and guest self-profiling.

## Risks and Test Signals
Risks include exposing cross-domain samples in the wrong mode, version mismatch, architecture-specific PMU field races, and LVTPC misprogramming. Test signals include mode transitions, perf sampling in guest/dom0 modes, BTS feature queries, PMU interrupt delivery, and cleanup on finish.
