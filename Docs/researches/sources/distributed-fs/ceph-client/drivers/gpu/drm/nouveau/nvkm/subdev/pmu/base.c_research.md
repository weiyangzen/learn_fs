# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/base.c

## Purpose
Provides common NVKM PMU subdevice construction, firmware interface loading, falcon queue setup, lifecycle hooks, fan-control policy, message send/receive wrappers, and interrupt dispatch.

## Important APIs, Types, And Functions
Exports `nvkm_pmu_fan_controlled`, `nvkm_pmu_pgob`, `nvkm_pmu_send`, `nvkm_pmu_ctor`, and `nvkm_pmu_new_`. Internal hooks include `nvkm_pmu_recv`, `nvkm_pmu_intr`, `nvkm_pmu_init`, `nvkm_pmu_fini`, and `nvkm_pmu_dtor`.

## Control Flow
Construction initializes mutex/workqueue/waitqueue state, loads the matching firmware interface via `nvkm_firmware_load`, constructs a falcon at base `0x10a000`, then creates queue manager, high-priority command queue, low-priority command queue, and message queue. Init/fini/intr delegate to generation function callbacks when present. Send returns `-ENODEV` if no PMU or send callback exists.

## State And Persistence
Persists `struct nvkm_pmu`, selected `pmu->func`, falcon state, command/message queues, send mutex, receive work/waitqueue, and `wpr_ready` completion. Destructor tears queue and falcon state down.

## Dependencies And Integration Points
Depends on `core/firmware.h`, falcon queue APIs, timer infrastructure, and generation `nvkm_pmu_fwif` tables. Other subdevices call PMU fan-control, PGO/B, and send wrappers.

## Risks And Test Signals
Risks include partial constructor failure leaks, firmware-interface mismatch, queue creation order, work item racing with teardown, and fan-control policy differences between internal and board firmware. Test PMU init/fini/unload, interrupt receive, command send/reply, firmware fallback, fan control exposure, and failure injection for each queue allocation.
