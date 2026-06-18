# sources/distributed-fs/ceph-client/sound/oss/dmasound/dmasound_q40.c

## Purpose

`dmasound_q40.c` is the Q40/Q60 low-level backend for the legacy dmasound OSS core. It provides a simple 8-bit DAC playback implementation, software conversion and sample-rate expansion/compression, interrupt-driven sample feeding, and machine registration guarded by `MACH_IS_Q40`.

## Important APIs, Types, and Functions

The machine descriptor `machQ40` supplies DMA allocation (`Q40Alloc`/`Q40Free`), IRQ lifecycle (`Q40IrqInit`, `Q40IrqCleanUp`), silence/init/format/volume/play callbacks, default settings, hardware formats, and capabilities. Translation tables are split into `transQ40Normal`, `transQ40Expanding`, and `transQ40Compressing`; each supports mu-law/A-law, signed 8-bit, and unsigned 8-bit only. Module entry is `dmasound_q40_init()` and exit is `dmasound_q40_cleanup()`.

## Control Flow

Module init checks `MACH_IS_Q40`, installs `machQ40` and defaults into the global core state, then calls `dmasound_init()`. IRQ init registers `Q40StereoInterrupt()` initially on `Q40_IRQ_SAMPLE`.

When the core prepares output, `Q40Init()` chooses hard speed from the two hardware rates, 10000 or 20000 Hz. If the requested soft speed falls within `catchRadius` of a hardware rate it snaps soft speed to that rate and uses direct conversion. If requested speed is too high it selects 20000 Hz and compression; otherwise it uses expansion. It forces 8-bit hard size and resets `expand_bal` for rate conversion.

`Q40Play()` starts playback only when no frame is active and there is either a full fragment or a sync/post condition. `Q40PlayNextFrame()` stores the current buffer pointer and byte count in `q40_pp`/`q40_sc`, advances the queue, derives the hardware speed bit, disables sample IRQs, frees the old handler, installs either mono or stereo IRQ handler based on `dmasound.soft.stereo`, writes sample-rate/clear/enable registers, and returns. The mono/stereo IRQ handlers write one or two bytes into `DAC_LEFT`/`DAC_RIGHT` per interrupt and call `Q40Interrupt()` when the frame is consumed. `Q40Interrupt()` clears active state, decrements queue count, tries to queue another frame, disables sample generation and centers DACs at 127 when empty, and wakes queue waiters.

## State and Persistence

The backend keeps global rate-conversion accumulators `expand_bal` and `expand_data`, plus active IRQ playback cursor `q40_pp` and count `q40_sc`. Hardware state lives in Q40 master/sample registers and DAC memory-mapped symbols. Buffers are allocated with `kmalloc()` through the core. There is no persistent storage.

## Dependencies and Integration Points

Dependencies include Q40 architecture interrupt and master/DAC headers, legacy OSS soundcard constants, and the `dmasound.h` queue/global contracts. It consumes the core's mu-law/A-law tables and calls `dmasound_init()`/`dmasound_deinit()`.

## Risks and Edge Cases

The IRQ handler is freed and re-requested for every frame to switch mono/stereo behavior, which is expensive and risk-prone if an error occurs; failed `request_irq()` is only rate-limited logged, not propagated to the core. `Q40IrqCleanUp()` frees with `Q40Interrupt` as dev_id, matching the request dev_id rather than the function pointer, but this pattern is subtle. Volume is a no-op. Only 8-bit formats are supported, so unsupported 16-bit writes move zero bytes via missing translation callbacks. Rate conversion is nearest-sample style and keeps state across calls, so reset/reinit behavior is important for glitches.

## Test Signals

Build on Q40 or compile-test capable m68k, module init on non-Q40 returning `-ENODEV`, direct 10 kHz and 20 kHz playback, expansion/compression path writes, mono and stereo IRQ handler switching, empty-queue DAC centering, `SNDCTL_DSP_SYNC` drain wakeups, and robustness when IRQ re-request fails.
