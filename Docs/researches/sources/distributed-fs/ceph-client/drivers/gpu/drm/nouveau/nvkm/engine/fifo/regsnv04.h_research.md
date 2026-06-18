# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/regsnv04.h

Purpose: defines legacy PFIFO register offsets and bitfields used by NV03/NV04 through NV50-era FIFO code. It centralizes interrupt, RAMHT/RAMFC/RAMRO, cache, DMA fetch, semaphore, acquire, method/data, and CHID mask constants.

Important APIs and data: macros include `NV03_PFIFO_INTR_0`, `NV03_PFIFO_INTR_EN_0`, `NV_PFIFO_INTR_*` bits, `NV03_PFIFO_RAMHT/RAMFC/RAMRO`, `NV03_PFIFO_CACHES`, `NV04_PFIFO_MODE`, `NV50_PFIFO_CTX_TABLE()`, cache push/pull registers, DMA fetch trigger/size/max request encodings, endian bits, acquire/semaphore registers, and method/data address macros for NV04 and NV40 layouts.

Control flow: no executable flow exists. Consumers use these constants to initialize PFIFO, save/restore RAMFC layouts, decode and acknowledge interrupts, advance cache GET/PUT pointers, and recover from DMA/cache errors.

State and persistence: macros describe hardware state locations. Runtime state is in PFIFO registers and instance memory managed by the C files.

Dependencies and integration: included by NV04/NV10/NV17/NV40 legacy FIFO implementations. The constants must match hardware manuals/reverse-engineered behavior.

Risks: bad offsets or masks cause hardware hangs or silent corruption. Some symbolic names alias different generation semantics, so consumers must choose generation-correct macros. Large DMA fetch encoding tables are easy to misuse.

Test signals: successful compile, correct legacy PFIFO init values, cache-error recovery using the expected method/data address space, and no regressions in NV04/NV10/NV17/NV40/NV50 interrupt handling.
