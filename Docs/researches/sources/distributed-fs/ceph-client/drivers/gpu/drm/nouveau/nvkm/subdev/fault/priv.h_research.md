<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/priv.h

## Purpose
Private interface for the NVKM fault subdevice. It defines replayable fault buffer objects, the generation-specific fault function table, and prototypes shared by GP100/GV100/TU102 implementations and the user object wrapper.

## Important APIs, Types, And Functions
`struct nvkm_fault_buffer` binds an NVKM object to a hardware fault buffer, cached get/put MMIO offsets, backing `nvkm_memory`, BAR address, and interrupt handle. `struct nvkm_fault_func` supplies subdevice lifecycle hooks, per-buffer hooks (`info`, `pin`, `init`, `fini`, `intr`), and the user class selector. Prototypes include `nvkm_fault_new_()`, GP100 buffer helpers, `gv100_fault_buffer_process()`, `gv100_fault_oneinit()`, and `nvkm_ufault_new()`.

## Control Flow
This header is declarative. Constructors choose a concrete `nvkm_fault_func`, the core uses it to allocate buffers and run lifecycle callbacks, and user-class creation later exposes the selected replayable buffer through `nvkm_ufault_new()`.

## State And Persistence
The buffer structure stores persistent runtime state for the lifetime of the fault subdevice: allocated memory, address, entry count, get/put register offsets, and interrupt registration. The header itself stores no state.

## Dependencies And Integration Points
Depends on `subdev/fault.h`, NVKM event/object infrastructure, memory allocation, interrupt handles, FIFO fault reporting, and MMU/GSP-generation code. It is the private contract between `base.c`, generation fault implementations, and `user.c`.

## Risks
The `user.rp` index, `entry_size`, and get/put register offsets must match hardware and user ABI expectations. Function-table holes or mismatched buffer counts can produce unmappable buffers, lost interrupts, or replayable faults that userspace cannot drain.

## Test Signals
Build coverage catches prototype drift. Runtime signals are successful fault subdevice oneinit/init, valid user object creation, event delivery on pending buffers, and FIFO fault reports with sane decoded fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/priv.h -->
