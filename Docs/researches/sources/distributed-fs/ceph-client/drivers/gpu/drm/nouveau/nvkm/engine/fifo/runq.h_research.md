# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runq.h

Purpose: declares the FIFO runqueue/PBDMA abstraction and its callback contract.

Important APIs and data: `struct nvkm_runq_func` has callbacks for init, interrupt handling, PBDMA INTR0 names, HCE CTXNOTVALID handling, and idle checks. `struct nvkm_runq` stores the callback table, owning FIFO, PBDMA id, and list node. Macros provide runqueue iteration and prefixed logging.

Control flow: chip-specific FIFO tables point `.runq` at a `nvkm_runq_func`; common construction creates runqueues; interrupt handlers iterate matching runqueues and call `runq->func->intr()`.

State and persistence: runtime in-memory only. Hardware state is owned by chip-specific callbacks.

Dependencies and integration: included by GF100/GK104/GK208/GV100 FIFO paths and generic runqueue construction.

Risks: optional callbacks require guards; missing idle callback limits recovery on preempt-capable runlists; logging macro assumes valid FIFO/subdev pointers.

Test signals: compile-time callback consistency, PBDMA interrupt logs with correct id, idle polling during recovery, and no NULL callback dereferences on older hardware.
