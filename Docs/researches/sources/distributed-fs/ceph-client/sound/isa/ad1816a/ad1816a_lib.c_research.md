# sources/distributed-fs/ceph-client/sound/isa/ad1816a/ad1816a_lib.c

## Purpose

`ad1816a_lib.c` is the low-level ALSA implementation for AD1816A-family codecs. It owns register I/O, codec probing, IRQ handling, ISA DMA programming, PCM open/prepare/trigger/pointer callbacks, timer support, mixer controls, and PM register image save/restore.

## Important APIs, Types, and Functions

- Register helpers `snd_ad1816a_busy_wait()`, `snd_ad1816a_in()`, `snd_ad1816a_out()`, `snd_ad1816a_read()`, `snd_ad1816a_write()`, and mask variants serialize access through the chip status and indirect register window.
- `snd_ad1816a_create()` requests the I/O region, IRQ, and two DMA channels, initializes `struct snd_ad1816a`, probes chip version, and resets runtime registers.
- PCM APIs are exported through `snd_ad1816a_pcm()` and the playback/capture ops tables. Prepare callbacks program DMA, sample rate, format, and period count.
- `snd_ad1816a_interrupt()` acknowledges playback, capture, and timer interrupts and calls `snd_pcm_period_elapsed()` or `snd_timer_interrupt()`.
- `snd_ad1816a_timer()` exposes the codec timer through `struct snd_timer_hardware`.
- `snd_ad1816a_mixer()` creates controls from `snd_ad1816a_controls[]`, including volume TLVs, mute switches, capture source, capture gain, mic boost, and 3D controls.
- PM functions save 48 indirect registers into `chip->image[]` and restore them after reinitialization.

## Control Flow

Creation initializes resource sentinels, reserves ports/IRQ/DMA, stores the card and base port, initializes the spinlock, probes the version register, then calls `snd_ad1816a_init()` to disable interrupts, disable playback/capture PIO, enable WSS-related bits, clear DSP config, and power up the chip. PCM open calls `snd_ad1816a_open()` to reject duplicate mode use and enable the appropriate interrupt bit. Prepare disables the stream, programs ISA DMA with autoinit, scales the sample rate when `clock_freq` is set, writes sample format and base count, and returns. Trigger only toggles the playback or capture enable bit. Interrupt handling reads status under the lock, notifies ALSA streams outside that first critical section, then writes interrupt status to acknowledge.

## State and Persistence Behavior

`struct snd_ad1816a` holds the hardware base port, IRQ, DMA channels, current open modes, playback/capture substream pointers, DMA buffer sizes, timer pointer, chip version/hardware ID, optional clock override, and PM register image. The mode bitmask prevents concurrent opens of the same stream or timer and is cleared fully when no open mode remains. Hardware settings are stored in chip registers and are reprogrammed on each prepare; PM persists register values only in memory across suspend.

## Dependencies and Integration Points

This file depends on ISA DMA helpers from `<asm/dma.h>`, ALSA PCM/timer/control APIs, device-managed resource helpers called by the card driver, and register constants from `<sound/ad1816a.h>`. It is consumed by the card-level AD1816A driver and any other code including the AD1816A header exports. It presents normal ALSA PCM, mixer, and timer objects to userspace.

## Risks and Edge Cases

Register access ignores the return value of `snd_ad1816a_busy_wait()` in most helpers, so timed-out hardware may still be read/written after a warning. The period register uses `period_bytes / 4 - 1`; unusual formats or period sizes must match hardware expectations. Playback and capture share the same enable bit value but different registers, which the trigger code handles with an `iscapture` flag. The IRQ handler always returns `IRQ_HANDLED` after acknowledging, so shared-IRQ false positives are not distinguished. Mixer put paths mask user values but rely on ALSA control ranges to keep semantics sane.

## Test Signals

Tests should cover chip version identification, resource rejection on busy ports/IRQs/DMA, playback and capture at supported formats/rates/channels, period interrupts, pointer movement, timer ticks, mixer read/write change reporting, capture source validation, and suspend/resume restoring mixer values. Runtime debug signals include "chip busy" warnings and absence of PCM period callbacks when interrupts are misconfigured.
