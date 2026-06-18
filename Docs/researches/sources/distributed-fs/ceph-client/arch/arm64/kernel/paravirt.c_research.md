# sources/distributed-fs/ceph-client/arch/arm64/kernel/paravirt.c

Purpose: Enables arm64 paravirtualized stolen-time accounting through SMCCC hypervisor calls.

Important APIs and state: per-CPU `stolen_time_region` stores an RCU-protected mapped `pvclock_vcpu_stolen_time` pointer. `para_steal_clock()` returns stolen time in ns. `pv_time_init()` probes hypervisor support, registers CPU hotplug callbacks, updates the `pv_steal_clock` static call, and enables static keys. Early param `no-steal-acc` disables runqueue steal accounting.

Control flow: CPU online calls SMCCC `ARM_SMCCC_HV_PV_TIME_ST`, remaps the returned stolen-time structure, validates revision/attributes, and publishes it under RCU. CPU down removes the pointer, synchronizes RCU, and unmaps. Reads return zero until the CPU mapping exists.

Dependencies and integration: depends on SMCCC 1.1, PSCI/hypervisor PV time ABI, CPU hotplug, RCU, memremap, static calls, scheduler cputime accounting, and static keys in paravirt core.

Risks and test signals: risks are mapping invalid hypervisor addresses, stale RCU pointers on CPU down, revision/attribute mismatch, and enabling accounting despite user opt-out. Test on hypervisors with and without PV time, CPU hotplug, scheduler steal-time accounting, `no-steal-acc`, and malformed hypervisor return handling.
