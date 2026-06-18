# sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx_core.c

## Purpose
This file implements the low-level LX6464ES PLX/DSP register access, MicroBlaze mailbox protocol, pipe/stream/buffer/gain commands, peak metering, and interrupt handling.

## Important APIs, Types, and Functions
`lx_dsp_reg_read/write()` and `lx_plx_reg_read/write()` map symbolic register enums to MMIO/I/O offsets. `lx_message_init()` and `lx_message_send_atomic()` build and synchronously submit `struct lx_rmh` commands using the `dsp_commands[]` table. Public DSP helpers include `lx_dsp_get_version()`, `lx_dsp_get_clock_frequency()`, `lx_dsp_set_granularity()`, `lx_dsp_read_async_events()`, and `lx_dsp_get_mac()`. Pipe/stream/buffer APIs include `lx_pipe_allocate/release/start/pause/stop/state/sample_count`, `lx_stream_set_format/state/sample_position`, `lx_buffer_ask/give/free/cancel`, `lx_level_unmute()`, and `lx_level_peaks()`. IRQ APIs are `lx_interrupt()`, `lx_threaded_irq()`, `lx_irq_enable()`, and `lx_irq_disable()`.

## Control Flow
ALSA-facing code calls pipe allocation and stream format/state helpers during prepare/trigger. Each command locks `msg_lock`, initializes the mailbox header, writes command words to CRM registers, sets the CSM command bit, polls for response, reads status words, clears the response bit, and returns firmware status or Linux errors. The hard IRQ acknowledges PLX doorbells, records async IRQ sources, and wakes the thread. The threaded IRQ reads async events, derives input/output EOB pipe masks, asks firmware for buffer status, gives the next ALSA period DMA address, advances `frame_pos`, and notifies ALSA.

## State and Persistence
State is held in hardware registers, `chip->rmh`, `chip->irqsrc`, `chip->mac_address`, and `lx_stream.frame_pos`. Commands are synchronous and serialized. There is no persistence beyond runtime hardware/driver state.

## Dependencies and Integration Points
This file depends on `lx6464es.h` for device state, `lx_core.h`/`lx_defs.h` for command/register constants, Linux PCI/MMIO/delay helpers, ALSA period notification through `snd_pcm_period_elapsed()`, and buffer addresses supplied by the PCM layer.

## Risks
The mailbox send path busy-polls up to 40 ms and runs under a mutex; long DSP stalls can block PCM/control/proc callers. Firmware status codes are returned directly in some paths, mixing positive DSP errors with negative Linux errors. IRQ buffer replenishment calculates period size as `channels * 3 * period_size`; this must match DMA format programming. The threaded IRQ calls `snd_pcm_period_elapsed()` without checking whether `lx_stream->stream` is non-NULL, so teardown races rely on IRQ synchronization and locks. `lx_dsp_get_mac()` has a TODO for endian handling.

## Test Signals
DSP commands should complete without `ED_DSP_TIMED_OUT` or `ED_DSP_CRASHED`. Pipe state waits should reach `PSTATE_RUN` and `PSTATE_IDLE` within 50 ms. EOB interrupts should produce `CMD_04_GET_EVENT` masks and successful buffer give operations. Peak metering should map 4-channel groups into 64 values. Tests should stress full-duplex start/stop/hw_free while interrupts are active to catch stale stream pointer or frame position issues.
