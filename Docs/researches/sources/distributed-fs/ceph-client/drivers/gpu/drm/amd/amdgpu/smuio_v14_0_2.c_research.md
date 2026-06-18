# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v14_0_2.c

Purpose: SMUIO v14.0.2 operations for ROM offsets and a coherent 64-bit GPU clock counter read.

Important APIs, types, and functions: defines `smuio_v14_0_2_funcs` with ROM index/data callbacks and `get_gpu_clock_counter`.

Control flow: ROM helpers return SOC15 offsets. Clock-counter helper disables preemption, reads upper, lower, then upper again from golden TSC registers, rereads lower if upper changed, reenables preemption, and combines high/low into a 64-bit value.

State and persistence: state is hardware ROM and golden TSC counter registers. No software persistence.

Dependencies and integration points: used by timing/profiling code and ROM access paths through `amdgpu_smuio_funcs`; depends on v14.0.2 generated SMUIO headers and Linux preemption control.

Risks and test signals: the double-read handles rollover but only if registers behave as expected. Preemption is disabled briefly, so the path should stay fast. Test signals are monotonic clock counter reads, rollover behavior, and successful ROM offset use.
