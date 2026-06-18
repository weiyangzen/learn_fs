# sources/distributed-fs/ceph-client/arch/s390/include/asm/hiperdispatch.h

Purpose: This header declares s390 HiperDispatch topology control hooks.

Important APIs/types/functions: `hd_reset_state()`, `hd_add_core(int cpu)`, `hd_disable_hiperdispatch()`, and `hd_enable_hiperdispatch()` are the public functions.

Control flow: Topology or CPU bring-up code resets state, records cores as CPUs appear, and enables or disables HiperDispatch according to platform capability and policy.

State and persistence: Persistent state is maintained by the implementation, likely CPU/core topology and dispatch enablement state; this header only exposes lifecycle entry points.

Dependencies and integration points: It integrates CPU topology management, scheduler capacity/placement logic, and IBM Z firmware/hypervisor dispatch hints.

Risks and test signals: Incorrect core accounting can degrade scheduling or target unavailable dispatch state. Tests should cover boot on LPAR/zVM/KVM, CPU hotplug, HiperDispatch disable fallback, and topology reporting.
