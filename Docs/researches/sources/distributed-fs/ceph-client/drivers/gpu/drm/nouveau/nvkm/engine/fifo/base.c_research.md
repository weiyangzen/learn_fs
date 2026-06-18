<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/base.c

## Purpose

`fifo/base.c` implements the generic FIFO engine lifecycle, class exposure, runlist/runqueue setup, interrupt/event registration, USERD allocation, engine info queries, pause/start/fault wrappers, and teardown.

## Important APIs, Types, And Functions

`nvkm_fifo_ctxsw_in_progress()` checks engine context-switch state across runlists. `nvkm_fifo_pause()`, `nvkm_fifo_start()`, and `nvkm_fifo_fault()` dispatch generation callbacks. `nvkm_fifo_class_new()` routes user class creation to channel-group or channel constructors. `nvkm_fifo_info()` answers NV_DEVICE_HOST channel/runlist/engine queries. `nvkm_fifo_oneinit()` creates global or per-runlist CHID allocators, runqueues, runlists, interrupt handlers, nonstall events, and shared USERD BAR1 memory. `nvkm_fifo_init()` initializes PBDMAs, runqueues, runlists, generation state, and enables interrupts. `nvkm_fifo_fini()` blocks interrupts and finalizes runlists. `nvkm_fifo_new_()` initializes the engine object and locks.

## Control Flow

Generation probe calls `nvkm_fifo_new_()`. Oneinit creates scheduler structures and events based on the generation `nvkm_fifo_func`. Runtime init programs runqueues/runlists and enables interrupts. User class enumeration exposes channel-group and channel classes. Teardown frees USERD mappings, runlists, runqueues, CHID/CGID allocators, nonstall events, and generation private state.

## State And Persistence Behavior

Persistent FIFO state includes function table, runqueue/runlist lists, global CHID/CGID allocators, nonstall event, USERD memory and BAR1 VMA, locks, mutex, and timeout defaults. Runlist/channel state persists in child objects.

## Dependencies And Integration Points

It depends on MC interrupts, BAR1 VMM, MMU memory, GPU object helpers, runlist/runqueue/channel/group helpers, NVIF host info constants, and generation FIFO tables.

## Risks And Edge Cases

USERD allocation assumes global `fifo->chid` exists for BAR1-backed USERD generations. `nvkm_fifo_info()` must distinguish global and per-runlist CHID designs. Interrupt registration and nonstall event counts depend on generation callbacks. Teardown must block interrupt sources before freeing runlists.

## Test Signals

Signals include correct NV_DEVICE_HOST query results, successful channel/group class creation, runlist updates after channel insert/remove, nonstall event delivery, no USERD mapping leaks, and clean suspend/resume init/fini cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/base.c -->
