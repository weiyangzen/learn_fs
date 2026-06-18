# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_device.h

## Purpose
This header defines the central Panfrost device, feature, compatibility, per-file, MMU, and exception types shared by the driver.

## Important APIs, Types, and Functions
Key types are `struct panfrost_device`, `struct panfrost_features`, `struct panfrost_compatible`, `struct panfrost_mmu`, `struct panfrost_file_priv`, and `struct panfrost_engine_usage`. It defines PM feature bits, GPU quirks, component suspension bits, exception codes, address-space interrupt masks, helper predicates, and lifecycle/reset declarations.

## Control Flow
The header has inline flow for privilege checks, model comparison, Bifrost detection, exception fault classification, and reset work scheduling.

## State and Persistence Behavior
`struct panfrost_device` is the persistent DRM-device object and contains MMIO, IRQs, clocks, regulators, PM domains, feature registers, scheduler/job state, reset work, shrinker state, devfreq, cycle counter, and debugfs lists. `struct panfrost_file_priv` persists per DRM fd and owns an MMU context and JM contexts.

## Dependencies and Integration Points
It ties together DRM device/auth, DRM MM, GPU scheduler, regulator, PM, io-pgtable, devfreq, and job manager declarations. Most Panfrost `.c` files include it directly or indirectly.

## Risks
Because this header defines cross-subsystem shared state, layout or semantic changes have broad blast radius. Lock ownership for `as_lock`, `sched_lock`, shrinker locks, job locks, and debugfs locks must stay consistent. Exception values must match the UAPI and hardware encoding.

## Test Signals
Build coverage catches type drift. Runtime signals include correct fd private allocation/free, scheduler/debugfs/fdinfo access, MMU AS reuse, reset work scheduling, and fault classification in logs.
