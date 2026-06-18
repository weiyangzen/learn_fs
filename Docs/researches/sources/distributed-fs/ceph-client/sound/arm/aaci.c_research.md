# sources/distributed-fs/ceph-client/sound/arm/aaci.c

## Purpose
This file implements the ALSA driver for the ARM PrimeCell PL041 Advanced Audio CODEC Interface. It drives an AC'97 link, creates an ALSA card and PCM device, performs PIO FIFO transfers in IRQ context, exposes AC97 bus read/write operations, and supports basic suspend/resume power state notification.

## Important APIs, Types, And Functions
The AMBA driver entry points are `aaci_probe()` and `aaci_remove()` via `module_amba_driver()`, matching ID `0x00041041`. AC97 bus operations are `aaci_ac97_write()` and `aaci_ac97_read()`, with codec selection through `aaci_ac97_select_codec()`. PCM operations are shared open/close/hw_params/prepare/pointer helpers plus playback and capture trigger functions. `aaci_fifo_irq()` handles FIFO interrupts, copying data to or from the ALSA runtime buffer using 16-byte ARM load/store sequences. `aaci_probe_ac97()`, `aaci_init_card()`, `aaci_init_pcm()`, and `aaci_size_fifo()` build the card, codec, PCM, and hardware parameters.

## Control Flow
Probe requests AMBA regions, allocates an ALSA card, maps MMIO, initializes playback/capture runtime state to channel 0, disables FIFOs/IRQs, clears interrupts, enables the AC97 slot-control path, probes the AC97 codec, sizes the FIFO, creates PCM streams, and registers the card. PCM open selects playback or capture runtime, copies hardware constraints, loads AC97-supported rates, adds playback channel rules, and lazily requests the shared IRQ on the first open. `hw_params()` opens the assigned AC97 PCM slots and programs control flags for compact 16-bit transfer. Prepare initializes runtime buffer pointers and period byte counters. Trigger starts/stops channel FIFO control and interrupt enable bits. IRQ handling detects RX/TX service conditions, moves data between FIFO and ring buffer, updates period counters, and calls `snd_pcm_period_elapsed()` outside the spinlock when needed.

## State And Persistence
`struct aaci` holds card/device/MMIO, FIFO depth, user count, AC97 bus/codec, main control bits, and playback/capture runtimes. Each `aaci_runtime` persists channel base/fifo addresses, spinlock, AC97 PCM mapping, current control register, ALSA substream, period size, ring pointers, byte counter, and FIFO transfer size. IRQ allocation is tied to `aaci->users` and released when the last stream closes.

## Dependencies And Integration Points
The driver depends on AMBA bus APIs, ALSA core/PCM/AC97, PrimeCell PL041 register definitions from `aaci.h`, and ARM PIO semantics. It integrates with the ALSA AC97 layer through `snd_ac97_bus()`, `snd_ac97_mixer()`, and `snd_ac97_pcm_assign()`, and with device PM through `DEFINE_SIMPLE_DEV_PM_OPS`.

## Risks And Test Signals
The driver is PIO and IRQ heavy, so underrun/overrun and interrupt storm handling are primary risks. Inline ARM assembly assumes 16-byte FIFO transfers and ARM register conventions. Multi-channel playback supports 2/4/6 channels but 6-channel ordering requires userspace correction. Probe failure paths should be checked for iounmap/card/region cleanup. Test signals include AC97 register read/write reliability, FIFO depth detection multiple-of-16, first-open IRQ request and last-close free, playback/capture period notifications, channel rule enforcement, and no WARN on close/hw_free with enabled channels.
