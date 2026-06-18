# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_0.c

Purpose: SMUIO v15.0.0 operation table exposing only the GPU golden TSC clock counter.

Important APIs, types, and functions: defines `smuio_v15_0_0_funcs` with `get_gpu_clock_counter`.

Control flow: the counter read disables preemption, reads upper/lower/upper, rereads lower on upper rollover, reenables preemption, and returns a combined 64-bit counter.

State and persistence: state is the hardware golden TSC counter registers; no software state persists.

Dependencies and integration points: used by generic amdgpu timing paths through `amdgpu_smuio_funcs`; depends on SMUIO 15.0.0 generated register headers and preemption control.

Risks and test signals: no ROM/topology callbacks are provided, so callers must handle NULL operations. Test signals are monotonic counter reads and correct version dispatch.
