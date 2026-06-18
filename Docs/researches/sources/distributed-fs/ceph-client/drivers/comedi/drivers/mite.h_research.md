## sources/distributed-fs/ceph-client/drivers/comedi/drivers/mite.h

### Purpose
`mite.h` declares the local Comedi MITE DMA helper interface and the small public data structures shared between `mite.c` and NI board drivers.

### Important APIs, Types, And Functions
Core types are `struct mite_dma_desc`, `struct mite_ring`, `struct mite_channel`, and `struct mite`. The header declares all exported helper APIs for ring allocation, descriptor initialization, buffer-change handling, channel request/release, DMA prepare/arm/disarm, interrupt acknowledgement, completion checks, byte-in-transit reporting, attach, and detach. It also defines `MAX_MITE_DMA_CHANNELS` and window register constants `MITE_IODWBSR`, `MITE_IODWBSR_1`, `WENAB`, and `MITE_IODWCR_1`.

### Control Flow
The header has no implementation flow. It encodes the lifecycle expected by callers: attach MITE, allocate ring, respond to Comedi buffer changes, request a DMA channel, prepare and arm it, synchronize/acknowledge interrupts, release the channel, free the ring, and detach.

### State, Persistence, And Dependencies
`struct mite` persists PCI device identity, MITE MMIO mapping, channel array, channel count, FIFO size, and spinlock. Rings persist coherent descriptor memory and a device reference. Channels persist direction, completion, and current ring ownership. The header depends on spinlocks, DMA address types through included kernel headers, and forward declarations for Comedi and PCI types.

### Integration Points
NI Comedi drivers include this header to use `mite.c` without duplicating register details. The constants expose only MITE window registers used externally; most register definitions stay private in `mite.c`.

### Risks
Callers can directly mutate public structs, so ownership and locking conventions are implicit. Descriptor fields are fixed little-endian 32-bit values and assume DMA addresses fit the hardware format. `dir` is an integer expected to match Comedi direction constants.

### Test Signals
Compile all drivers that include `mite.h`, check exported symbol prototypes, exercise channel lifecycle with lockdep, validate descriptor endian layout, and test misuse cases such as release without ring, zero buffer size, and attach failure cleanup.
