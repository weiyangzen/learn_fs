# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/base.c

## Purpose
Implements the common NVKM fault subdevice: fault-buffer allocation/pinning, event setup, lifecycle dispatch, user object registration, and interrupt forwarding.

## Important APIs, types, and functions
Exports `nvkm_fault_new_()`. Important internals include `nvkm_fault_oneinit_buffer()`, `nvkm_fault_oneinit()`, event init/fini callbacks, subdev `init/fini/intr/dtor`, and `nvkm_event` management.

## Control flow
Oneinit allocates each generation-supported fault buffer, queries its entry count and get/put registers, allocates instance memory, pins it through the generation hook, then initializes per-buffer events. Event listeners enable or disable buffer interrupts. Init/fini and intr dispatch to generation hooks. Dtor removes notifications, finalizes events, unreferences memory, and frees buffers.

## State and persistence
`struct nvkm_fault` persists buffer pointers/count, event object, user-class data, and generation function table. Each `nvkm_fault_buffer` stores memory, BAR/device address, register offsets, id, and entries.

## Dependencies and integration points
Depends on `nvkm_memory_new()`, event infrastructure, subdev lifecycle, user fault constructor, and generation buffer hooks. Integrates with FIFO fault processing through generation code.

## Risks
Buffer memory pin failure returns `-EFAULT` after allocation; cleanup relies on dtor paths. Event enable directly controls hardware interrupts, so listener lifetime and buffer id must match.

## Test signals
Fault buffer allocation logs, user event subscription enabling/disabling interrupts, BAR/device address pinning, suspend/resume init/fini, and destructor leak checks.
