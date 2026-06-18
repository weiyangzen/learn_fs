# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_fw.h

`panthor_fw.h` defines the CSF firmware shared-memory ABI and the firmware management API consumed by scheduler, MMU, GEM, and PM paths.

It defines maximum CSG/CS counts, ringbuffer input/output interfaces, CS control/input/output structs, CSG control/input/output structs, global control/input/output structs, request/event/state masks, endpoint request encoding, timer and perfcnt fields, halt statuses, and wrapper structs with locks and typed pointers. It declares firmware init/unplug/reset, interface getters, endpoint request helpers, ack waits, CSG doorbells, queue interface memory allocation, suspend buffer allocation, and firmware VM access.

The core protocol is req/ack toggling: the host writes input bits so they differ from firmware ack bits, rings a doorbell, then waits for ack to match. `panthor_fw_toggle_reqs()`, `panthor_fw_update_reqs()`, and `panthor_fw_update_reqs64()` update shared input fields under spinlock because current uncached/write-combined mappings cannot safely use atomic cmpxchg.

The structs map persistent shared memory; host writes input, reads output/control, and scheduler interprets events. Dependencies are Panthor device/kernel BO declarations and uAPI-compatible bit layouts. Risks are layout drift, mask misuse between requests/events/config fields, and missing lock coverage. Test signals are firmware interface version boot, CSG start/suspend/resume, endpoint allocation, tiler OOM/resource events, global ping/idle/sleep, and ack timeouts.
