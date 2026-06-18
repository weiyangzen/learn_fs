# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_regs.h

`panfrost_regs.h` is the Panfrost Midgard/Bifrost MMIO contract. It defines GPU identity, feature, interrupt, command, performance-counter, coherency, power, job-slot, and MMU register offsets and bit fields, plus simple `gpu_write()` and `gpu_read()` helpers over `dev->iomem`.

Important macro groups include `GPU_ID` and feature registers, `GPU_INT_*` IRQ masks, `GPU_CMD_*` commands, `GPU_PERFCNT_*` and `GPU_PRFCNT_*` performance-counter registers, timestamp/cycle registers, coherency controls, shader/tiler/L2 present/ready/power registers, implementation config bits, `JS_*` job slot register generators, `MMU_*` and `AS_*` address-space registers, translation-table flags, and fault status masks.

The file has no executable control flow. Driver code uses these macros to probe features, start resets/cache/perfcnt commands, submit jobs, program MMU address spaces, poll power transitions, and decode faults. The macros name persistent hardware state: IRQ masks, job descriptors, AS translation tables, coherency protocol, and perfcnt configuration.

Dependencies are limited to kernel bit macros and the convention that the device object has an `iomem` mapping. Integration spans Panfrost GPU, job, MMU, perfcnt, power, and feature probing. Risks are severe for incorrect offsets or masks: bad definitions can corrupt MMIO state, hang job slots, break translations, or misreport counters. Test signals include boot and workload tests on Midgard/Bifrost, MMU fault handling, reset, power cycling, cache flushes, and perfcnt sampling.
