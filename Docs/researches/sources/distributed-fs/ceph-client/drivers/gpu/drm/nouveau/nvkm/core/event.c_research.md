# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/event.c

## Purpose
This file implements NVKM kernel event notification management. It tracks enabled event references per index/type, maintains notifier lists, gates hardware init/fini for events, and dispatches callbacks.

## Important APIs, Types, and Functions
Public functions include `__nvkm_event_init`, `nvkm_event_fini`, `nvkm_event_ntfy_add`, `nvkm_event_ntfy_del`, `nvkm_event_ntfy_allow`, `nvkm_event_ntfy_block`, `nvkm_event_ntfy`, and `nvkm_event_ntfy_valid`.

## Control Flow
Event init allocates a reference-count array sized by index and type count. Allowing a notifier atomically changes allowed state, increments per-type refs under `refs_lock`, calls backend init on first ref, and inserts wait-mode notifiers. Blocking reverses this and may remove wait-mode notifiers. Dispatch walks the notifier list under read lock and calls matching allowed callbacks.

## State and Persistence Behavior
State includes backend event function table, subdev pointer, refs array, notifier list, list lock, refs lock, notifier allowed/running flags, id, bits, wait flag, and callback.

## Dependencies and Integration Points
It depends on NVKM subdev logging and backend event init/fini functions. NVKM user events and NVIF events build on this layer.

## Risks
Reference counting must stay balanced or hardware events remain enabled/disabled incorrectly. Callback dispatch occurs under read lock/irq state, so callbacks must be safe. `nvkm_event_ntfy_valid` currently always returns true.

## Test Signals
Signals include allow/block ref transitions, wait-mode insertion/removal, concurrent dispatch and deletion, backend init/fini calls, and event teardown.
