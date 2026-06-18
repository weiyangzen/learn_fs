<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psci.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/psci.h

Purpose: defines ARM Power State Coordination Interface function IDs, power-state encodings, version/feature helpers, reset/off types, and return codes shared by kernel, KVM, and userspace.

Important APIs and types: macros build 32-bit and 64-bit PSCI function IDs for v0.2 through v1.3, including CPU suspend/on/off, affinity info, system off/reset/suspend/reset2/off2, mem protect, and statistics. Power-state masks describe original and extended suspend encodings. Version macros decode major/minor. Return constants include success, not supported, invalid params, denied, already on, on pending, disabled, not present, and invalid address.

Control flow: ARM firmware clients issue PSCI calls through SMC/HVC using these function IDs; KVM may emulate or forward calls for guests. Callers decode return values and feature bits to select supported behavior.

State and persistence: PSCI state is firmware/platform CPU and system power state. The header only defines call numbers and encodings.

Dependencies and integration points: integrates with ARM/arm64 boot, CPU hotplug, suspend/resume, KVM PSCI emulation, firmware interfaces, and userspace tooling that interprets PSCI IDs.

Risks and test signals: risks include wrong 32/64-bit function ID selection, power-state encoding mismatch, firmware version quirks, and KVM guest ABI drift. Test PSCI feature discovery, CPU on/off/suspend under KVM and hardware, reset/off paths, hibernate off type, and invalid parameter handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psci.h -->
