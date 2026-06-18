# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runl.h

Purpose: declares generic runlist and host-engine structures and callback contracts used by FIFO implementations.

Important APIs and data: `struct nvkm_engn_func` defines non-stall, channel-switch status, current channel/group ID, synthetic MMU fault, engine context construction/binding, RAMHT add/delete, and secondary constructor hooks. `struct nvkm_runl_func` defines init/fini, runqueue count, descriptor size, runlist update/insert/commit/wait/pending, block/allow, fault clear, preempt, and preempt-pending callbacks. `struct nvkm_runl` stores IDs, doorbell, CHID/CGID allocators, engine and group lists, runqueue pointers, interrupt hooks, memory, locks, and RC atomics.

Control flow: the header establishes how chip-specific FIFO code plugs into generic runlist management. Macros iterate runlists, engines, and channel groups and provide logging prefixes.

State and persistence: describes runtime-only in-memory state. No durable persistence exists.

Dependencies and integration: included by FIFO chip files, user channel code, and runlist implementation. It references `nvkm_engine`, `nvkm_fifo`, `nvkm_chid`, `nvkm_memory`, `nvkm_inth`, and Linux work/mutex/list primitives.

Risks: the fixed `runq[2]` array constrains current multi-runqueue support; callback nullability differs by generation; callers must respect lock/put protocols for lookup helpers.

Test signals: successful compilation of all FIFO variants, correct runlist logging prefixes, runqueue assignment not exceeding two entries, and runtime recovery paths invoking the intended callbacks.
