# sources/distributed-fs/ceph-client/drivers/gpu/trace/Makefile

Purpose: Kbuild fragment for GPU memory tracepoint provider.

Important targets: `obj-$(CONFIG_TRACE_GPU_MEM) += trace_gpu_mem.o`.

Control flow: no runtime flow; conditional compilation only.

State and persistence: no state.

Dependencies and integration: tied to the `TRACE_GPU_MEM` Kconfig symbol and `trace_gpu_mem.c`.

Risks: if tracepoint implementation grows into multiple objects, this Makefile must be updated.

Test signals: successful object build when `CONFIG_TRACE_GPU_MEM=y`.
