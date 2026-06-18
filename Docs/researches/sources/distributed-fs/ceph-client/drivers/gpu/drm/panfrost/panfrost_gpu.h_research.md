# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gpu.h

## Purpose
This header declares the Panfrost GPU block interface for initialization, reset, power, IRQ suspend, counters, flush-id reading, and vendor quirks.

## Important APIs, Types, and Functions
It declares `panfrost_gpu_init/fini`, `panfrost_gpu_get_latest_flush_id`, `panfrost_gpu_soft_reset`, `panfrost_gpu_power_on/off`, `panfrost_gpu_suspend_irq`, cycle counter get/put/read, timestamp read, and `panfrost_gpu_amlogic_quirk`.

## Control Flow
There is no executable flow. Device init/PM/reset/job paths call these functions to control GPU hardware and read counters.

## State and Persistence Behavior
The header stores no state. Implementations mutate `struct panfrost_device` feature, IRQ, power, and cycle-counter fields and hardware registers.

## Dependencies and Integration Points
It is used by device init/reset, ioctl timestamp queries, job profiling, fdinfo, compatible data vendor hooks, and GPU PM code.

## Risks
Callers must hold or acquire runtime PM as appropriate before reading hardware registers. Counter get/put calls must remain balanced around jobs and timestamp reads.

## Test Signals
Build coverage plus runtime reset, timestamp, profiling, PM, and compatible quirk tests validate the interface.
