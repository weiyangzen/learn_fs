# sources/distributed-fs/ceph-client/arch/s390/include/asm/kasan.h

Purpose: This header defines the s390 KASAN shadow address layout when KASAN is enabled.

Important APIs/types/functions: `KASAN_SHADOW_SCALE_SHIFT`, `KASAN_SHADOW_SIZE`, `KASAN_SHADOW_OFFSET`, `KASAN_SHADOW_START`, and `KASAN_SHADOW_END` are defined under `CONFIG_KASAN`.

Control flow: KASAN initialization and address translation use the configured shadow offset and region-size-derived shadow span to map kernel shadow memory.

State and persistence: The header defines address constants only; shadow memory state is allocated and managed by KASAN core and s390 memory setup.

Dependencies and integration points: It depends on page-table region shifts from the s390 MM layout and Linux KASAN configuration.

Risks and test signals: A wrong shadow range can overlap vmalloc/modules or miss instrumented memory. Tests should include KASAN boot, slab/page out-of-bounds detection, vmalloc/module accesses, and randomized-base configurations.
