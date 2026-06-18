# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio.h

## Purpose
Private interface for the UniPhier AIO sound driver. It centralizes stream names, hardware IDs, clock/PLL IDs, IEC61937 constants, data structures, and helper prototypes shared by UniPhier AIO DMA, DAI, port, SRC, and compressed-audio code.

## Important APIs, Types, and Functions
Key types are `enum ID_PORT_TYPE`, `enum ID_PORT_DIR`, `enum IEC61937_PC`, `struct uniphier_aio_selector`, `struct uniphier_aio_swmap`, `struct uniphier_aio_spec`, `struct uniphier_aio_pll`, `struct uniphier_aio_chip_spec`, `struct uniphier_aio_sub`, `struct uniphier_aio`, and `struct uniphier_aio_chip`. Helper prototypes include ring accounting, PLL/chip initialization, port/interface/SRC setup, DMA channel/ring setup, and `uniphier_aiodma_soc_register_platform()`.

## Control Flow, State, and Persistence
The header defines the state persisted across probe and stream runtime. `uniphier_aio_chip` owns platform resources, regmaps, reset/clock handles, active count, AIO instances, and PLL state. `uniphier_aio` stores per-DAI clock/PLL selections and two direction-specific `uniphier_aio_sub` objects. Each substream tracks PCM/compress pointers, parameters, mmap mode, running/setting flags, threshold, and 64-bit read/write origin/total counters protected by a spinlock.

## Dependencies and Integration Points
Depends on ALSA PCM/SoC/DAI declarations, Linux spinlocks/types, platform devices, and `aio-reg.h` users. It is the integration boundary among `aio-dma.c`, SoC descriptor files, common AIO DAI/control implementation, and the EVEA codec path.

## Risks and Test Signals
Risks include shared mutable substream fields touched from IRQ and PCM/compress callbacks, 64-bit offset wrap handling, aliasing compressed and PCM state in the same `uniphier_aio_sub`, and virtual mapping tables requiring exact SoC data. Test signals are build coverage across all UniPhier AIO objects, lockdep/IRQ testing around ring offsets, simultaneous playback/capture, compressed IEC61937 passthrough, and suspend/resume preserving chip and PLL state.
