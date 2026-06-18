# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-core.c

## Purpose
Implements the shared cx2388x core services used by analog video, ALSA, MPEG, DVB, input, and board modules. It builds RISC DMA programs, defines SRAM FIFO layouts, programs SRAM channels, provides debug/IRQ helpers, resets and shuts down hardware, computes scaling and TV norm register values, manages common analog audio DMA, initializes video devices, and owns shared-core reference management.

## Important APIs, Types, And Data
Exported APIs include `cx88_risc_buffer()`, `cx88_risc_databuffer()`, `cx88_sram_channels[]`, `cx88_sram_channel_setup()`, `cx88_sram_channel_dump()`, `cx88_print_irqbits()`, `cx88_core_irq()`, `cx88_wakeup()`, `cx88_shutdown()`, `cx88_reset()`, `cx88_set_scale()`, `cx88_start_audio_dma()`, `cx88_stop_audio_dma()`, `cx88_set_tvnorm()`, `cx88_vdev_init()`, `cx88_core_get()`, and `cx88_core_put()`. Module parameters `core_debug`, `nicam`, and `nocomb` adjust logging, audio assumptions, and comb filtering.

The SRAM layout table maps channels 21-28/27 to video Y/packed, U, V, VBI, audio in/out, MPEG, and audio RDS FIFOs with command/control/CDT/fifo register addresses. Global `cx88_devlist`, `cx88_devcount`, and `devlist` mutex maintain one shared core per PCI bus/slot across multiple PCI functions.

## Control Flow
RISC buffer creation estimates worst-case instruction storage, allocates coherent memory, and writes field/data transfer instructions through `cx88_risc_field()`. That helper walks DMA scatterlists line by line, emits resync/write instructions, splits lines at SG boundaries, optionally emits periodic IRQ/count increments, and leaves room for the caller to patch a loop jump. SRAM setup aligns bytes-per-line to 8 bytes, chooses up to six FIFO lines, writes CDT entries, programs command descriptors, and fills pointer/count registers.

`cx88_reset()` shuts down DMA and interrupts, clears status, initializes all SRAM channels with safe defaults, configures input/filter/FIFO/AGC defaults, resets onboard parts through `MO_SRST_IO`, and returns hardware to a baseline. `cx88_set_tvnorm()` refuses changes while video/VBI/MPEG queues are busy, computes PLL/subcarrier/AGC/HTOTAL/VBI/scaling values for PAL/NTSC/SECAM variants, calls `set_tvaudio()`, notifies I2C video subdevices, and grabs chroma AGC control for SECAM. `cx88_set_scale()` programs horizontal/vertical delay, scale, active size, and filter bits based on norm, field mode, input type, requested dimensions, and `nocomb`.

Audio helpers set up shared analog audio FIFOs unless ALSA downstream RISC DMA is already active. Shared IRQ handling currently dispatches IR sample interrupts and prints unexpected bits. Buffer wakeup timestamps and completes the first active vb2 buffer. `cx88_core_get()` either finds an existing core for the same PCI slot and reserves the MMIO resource for the requesting function, or calls `cx88_core_create()`. `cx88_core_put()` releases the function resource and destroys the core only when the refcount reaches zero.

## State And Persistence
Shared state is in `cx88_core`: MMIO mapping, board/tuner/input/tvnorm, current dimensions/field, V4L2 device/control handlers, I2C/IR state, DMA queues owned by higher layers, and refcount membership in `cx88_devlist`. Hardware state persists in cx2388x registers and SRAM command/FIFO areas while the device is active. RISC memory is coherent DMA memory owned by callers and freed by buffer finish paths. `cx88_start_audio_dma()` can leave audio FIFOs running for analog audio detection/playthrough, unless ALSA owns downstream RISC mode.

## Dependencies And Integration Points
This file is central to all cx88 modules. It depends on the shared `cx88.h` register macros, V4L2/vb2, PCI resource management, I2C subdevice notification via `call_all()`, audio standard helpers from `cx88-tvaudio.c`, IR helpers from `cx88-input.c`, and board creation from `cx88-cards.c`. ALSA uses `SRAM_CH25` and `cx88_risc_databuffer()`, DVB/Blackbird use MPEG SRAM and buffer completion paths through cx8802, and analog video uses video/VBI RISC and scaling/norm helpers.

## Risks And Test Signals
Risks include RISC size underestimation, SG-boundary mistakes, FIFO line counts below hardware requirements, TV norm register regressions, racey norm changes if busy checks miss a queue, core refcount/resource leaks across PCI functions, and audio DMA conflicts between ALSA and analog audio paths. Test signals are DMA capture across packed/planar/VBI/audio/MPEG users, `cx88_sram_channel_dump()` consistency during debug, no RISC bus-error IRQs, correct image geometry for multiple norms/fields/sizes, stable audio after norm/input changes, and clean probe/remove ordering for video, audio, DVB, and Blackbird modules.
