# sources/distributed-fs/ceph-client/include/linux/comedi/comedi_isadma.h

Purpose: This header defines ISA DMA helper state and APIs for Comedi drivers that use legacy ISA DMA channels.

Important APIs/types/functions: It defines direction constants `COMEDI_ISADMA_READ` and `COMEDI_ISADMA_WRITE`, `struct comedi_isadma_desc` with virtual address, bus address, channel, sizes, and mode, and `struct comedi_isadma` with device, descriptor count, current descriptor, primary/secondary channels, and flexible descriptor array. APIs include `comedi_isadma_program`, `comedi_isadma_disable`, `comedi_isadma_disable_on_sample`, `comedi_isadma_poll`, `comedi_isadma_set_mode`, `comedi_isadma_alloc`, and `comedi_isadma_free`; disabled `CONFIG_ISA_DMA_API` stubs do nothing or return `0`/`NULL`.

Control flow: Drivers allocate DMA descriptors, set transfer mode, program a descriptor, poll progress or disable on sample boundaries, and free descriptors at detach. The helpers abstract unavailable `<asm/dma.h>` constants.

State and persistence behavior: DMA state is tracked in descriptor buffers, hardware DMA channel programming, current descriptor index, and transfer sizes. Disabled builds allocate nothing and perform no DMA operations.

Dependencies and integration points: It includes `<linux/types.h>` and integrates Comedi drivers with legacy ISA DMA API, non-coherent memory allocation, and acquisition buffer movement.

Risks: ISA DMA has strict channel, size, and addressability constraints. Direction mistakes can corrupt memory or miss samples. Stubbed builds require graceful fallback. Descriptor lifetime must outlive active DMA.

Test signals: ISA-capable hardware tests, DMA residue/poll validation, disable-on-sample behavior, allocation failure paths, config-off builds, and buffer integrity checks are important.
