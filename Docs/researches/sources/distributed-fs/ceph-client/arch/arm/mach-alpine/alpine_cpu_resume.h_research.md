# sources/distributed-fs/ceph-client/arch/arm/mach-alpine/alpine_cpu_resume.h

Purpose: defines the memory-mapped CPU resume register layout used by Alpine firmware: global watermark/flags and a flexible per-CPU array containing flags and resume addresses.

Control flow is structural only. Runtime users validate `AL_CPU_RESUME_MAGIC_NUM_MASK` against `AL_CPU_RESUME_MAGIC_NUM` before writing resume addresses. Persistent state is the firmware-owned MMIO block. Dependencies are firmware ABI and `alpine_cpu_pm.c`. Risks are layout mismatch with firmware, missing flexible-array bounds checks, and magic-number changes. Test signals include successful watermark validation and secondary CPUs jumping to the programmed resume address.
