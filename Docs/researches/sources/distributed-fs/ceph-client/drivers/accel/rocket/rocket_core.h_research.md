# sources/distributed-fs/ceph-client/drivers/accel/rocket/rocket_core.h

Purpose: defines the per-core Rocket hardware abstraction and MMIO helper macros.

Important APIs and types: `struct rocket_core` stores device pointers, index, IRQ, register bases, clocks, resets, IOMMU group, job lock, in-flight job, fence state, reset workqueue, DRM scheduler, fence context, and sequence numbers. Macros wrap PC/CNA/CORE register reads/writes using generated offsets.

Control flow: callers use the macros when submitting, interrupting, and resetting jobs. Lifecycle functions are declared for core init/fini/reset.

State and persistence: the struct is persistent per detected NPU core and is owned by `rocket_device`.

Dependencies and integration: includes DRM scheduler, Linux clock/reset/io primitives, mutex types, and `rocket_registers.h`.

Risks and test signals: check offset arithmetic for CNA/CORE base-relative registers, lock ordering around `in_flight_job`, and scheduler/fence field initialization before use.
