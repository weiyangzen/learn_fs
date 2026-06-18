# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_core.c

## Purpose

This file is the low-level hardware transport for PCXHR cards. It owns PLX and DSP register access, Xilinx and DSP firmware loading primitives, RMH DSP command serialization, pipe start/stop sequencing, register-control caching, interrupt acknowledgement, asynchronous error decoding, and timer-driven PCM pointer updates.

## Important APIs, Types, And Functions

- Register macros map DSP and PLX mailbox/register offsets to the appropriate I/O BAR.
- `pcxhr_check_reg_bit()` waits for hardware status bits with jiffies-based timeouts.
- `pcxhr_send_it_dsp()` sends host interrupts/commands to the DSP and handles required HF0/HF1/HF5 handshakes.
- Firmware primitives include `pcxhr_reset_xilinx_com()`, `pcxhr_reset_dsp()`, `pcxhr_enable_dsp()`, `pcxhr_load_xilinx_binary()`, `pcxhr_load_eeprom_binary()`, `pcxhr_load_boot_binary()`, and `pcxhr_load_dsp_binary()`.
- `pcxhr_dsp_cmds[]`, `pcxhr_init_rmh()`, `pcxhr_set_pipe_cmd_params()`, and `pcxhr_send_msg()` implement the RMH command protocol.
- `pcxhr_set_pipe_state()` starts/stops playback and capture pipes using can-start, configure, IRQ fire, polling, and stop commands.
- `pcxhr_write_io_num_reg_cont()` serializes and caches writes to the main IO control register.
- `pcxhr_interrupt()` and `pcxhr_threaded_irq()` are the hard and threaded interrupt handlers.

## Control Flow

Firmware load starts with reset and bit-banged Xilinx transfer, then 24-bit DSP boot/eeprom/main-image transfer through HI08-style registers. Main DSP load is followed by higher-level board initialization in `pcxhr_hwdep.c`.

Normal DSP commands go through `pcxhr_send_msg()`, which takes `msg_lock`, sends the message interrupt, waits for `CHK`, resets the semaphore, writes command words, waits for completion, reads fixed/argument/mask-sized status words, and resets the semaphore again. This serialization is required because the DSP mailbox is a single command channel shared by PCM, mixer, firmware, proc, and IRQ-thread paths.

Pipe state changes first compute a combined playback/capture audio mask from requested masks and current MBOX2 state. Starts are prepared with `CMD_CAN_START_PIPE` retries, toggled with `CMD_CONF_PIPE`, committed with `CMD_SEND_IRQA`, then polled until MBOX2 reflects the new state. Stops are toggled and followed by `CMD_STOP_PIPE`.

The hard IRQ confirms the PLX doorbell belongs to this device, clears it, records the source bits, and wakes the threaded handler for timer or message-worthy events. The threaded handler updates stream positions from DSP time MBOX4, handles wrap/resync cases, calls `snd_pcm_period_elapsed()` outside the manager lock when needed, and runs `pcxhr_msg_thread()` to clear frequency/timecode events or decode async xrun reports.

## State And Persistence

The file updates `mgr->dsp_loaded` indirectly through firmware callers, `mgr->io_num_reg_cont`, `timer_toggle`, `dsp_time_last`, `dsp_time_err`, `src_it_dsp`, and async error counters. Stream timer fields are updated here under `mgr->lock`. State is volatile and hardware-derived.

## Dependencies And Integration Points

It depends on low-level Linux I/O port access, firmware structures, PCI devices, ALSA period notification, and shared PCXHR structures. Higher layers depend on this file for every DSP command and for precise PCM pointer progress.

## Risks

- Timeout loops are hardware-sensitive. Too-short waits cause false failures; too-long waits can stall kernel paths.
- `pcxhr_send_msg_nolock()` rejects `cmd_len >= PCXHR_SIZE_MAX_CMD`, so callers must stay inside the command buffer limit.
- The RMH status reader computes variable status length from the first returned word; malformed firmware status can overrun expected protocol and truncate.
- Timer update unlocks and relocks around `snd_pcm_period_elapsed()`, so stream lifetime and status must remain valid across callback re-entry.
- Any direct use of `pcxhr_send_msg_nolock()` must already hold `msg_lock`.
- Interrupt source is stored in a single `src_it_dsp` field; if hardware posts events faster than the thread handles them, source coalescing assumptions matter.

## Test Signals

Validation requires firmware load on real hardware, DSP command timeout/error-path tests, ALSA playback/capture pointer monotonicity, linked stream start/stop, xrun async counter tests, external clock/frequency-change IRQs, and stress tests with mixer writes while PCM streams run.
