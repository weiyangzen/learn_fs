# sources/distributed-fs/ceph-client/sound/arm/aaci.h

## Purpose
This private header defines PL041 AACI register offsets, bit masks, and driver-private runtime structures used by `aaci.c`.

## Important APIs, Types, And Functions
Register offsets cover per-channel control/status/interrupt registers, AC97 slot registers, interrupt clear, main control, reset, sync, main flags, and FIFO data registers. Bit masks define FIFO control (`CR_FEN`, `CR_COMPACT`, slot enables, sample size, `CR_EN`), status/interrupt bits, slot flags, interrupt clear bits, main control bits, reset/sync flags, and main busy flags. `struct aaci_runtime` tracks a stream's channel base, FIFO, spinlock, AC97 PCM, substream, control register, period and PIO buffer pointers. `struct aaci` stores AMBA/ALSA/card-wide state, AC97 objects, main control, runtime objects, and PCM pointer.

## Control Flow
The header is declarative. `aaci.c` uses offsets and bit definitions to program the device and uses the structures to coordinate probe, PCM callbacks, and IRQ handling.

## State And Persistence
The persistent state definitions mirror hardware and ALSA runtime state. `aaci_runtime` is per direction; `aaci` is per AMBA device/card.

## Dependencies And Integration Points
It depends on ALSA AC97/PCM structures and AMBA device structures through `aaci.c` includes. The register map is the integration point between the driver and ARM DDI 0173B PL041 hardware.

## Risks And Test Signals
Incorrect bit definitions would surface as AC97 access failures, FIFO stuck busy, or missing interrupts. Tests should cover register programming paths in probe, AC97 read/write, playback/capture triggers, and FIFO IRQ service.
