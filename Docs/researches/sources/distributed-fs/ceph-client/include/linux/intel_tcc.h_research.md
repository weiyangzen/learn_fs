<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_tcc.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_tcc.h

Purpose: Declares Intel Thermal Control Circuit helpers for CPU temperature and TjMax offset handling.

Important APIs/types/functions: `intel_tcc_get_tjmax()`, `intel_tcc_get_offset()`, `intel_tcc_set_offset()`, `intel_tcc_get_temp()`, and `intel_tcc_get_offset_mask()`.

Control flow: Thermal and platform drivers query TjMax/offset, optionally set offset, and read package or core temperatures.

State/persistence: TCC offset is hardware/MSR state; temperature readings are transient.

Dependencies/integration: Integrates CPU thermal drivers, MSR/platform code, and thermal zones.

Risks: Offset writes affect thermal throttling behavior; CPU/package selection must be correct.

Test signals: Per-CPU TjMax reads, offset mask enforcement, set/get offset roundtrip where permitted, core/package temperature reads, and unsupported CPU errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_tcc.h -->
