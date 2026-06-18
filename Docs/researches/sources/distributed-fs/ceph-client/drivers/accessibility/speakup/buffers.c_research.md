# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/buffers.c Research

## Purpose
`buffers.c` implements Speakup's fixed-size speech synthesis ring buffer and TTY throttling hooks. It queues `u16` characters for the active synthesizer and helps prevent console writers from outrunning speech output.

## Important APIs And Control Flow
Exported functions are `speakup_start_ttys()`, `synth_buffer_empty()`, `synth_buffer_getc()`, `synth_buffer_peek()`, `synth_buffer_skip_nonlatin1()`, and `synth_buffer_clear()`. `synth_buffer_add()` drops data if `synth->alive` is false, starts the synth and stops TTYs when free space falls below 100 entries, drops the new character when only one slot is free, otherwise writes to `buff_in`, wraps at `buffer_end`, and clears `spk_paused`. Readers consume or inspect `buff_out`.

## State And Persistence
The state is a static `u16 synth_buffer[8192]` plus `buff_in`, `buff_out`, and `buffer_end`. It is volatile and module-lifetime only. TTY stopped state lives in VT/TTY structures and is affected by stop/start calls.

## Dependencies And Integration Points
This file depends on `speakup_console`, `vc_cons`, `synth`, `synth_start()`, `spk_paused`, and kernel TTY helpers. It integrates with the Speakup synth thread and console ingestion path.

## Risks
The ring buffer has no internal locking; callers must use the Speakup locking discipline. If the synth dies after TTYs are stopped, recovery depends on later `speakup_start_ttys()` from a live context. Buffer pressure drops characters when full. The `speakup_start_ttys()` guard around `tty_stopped` should be reviewed with console state semantics.

## Test Signals
Stress high-volume console output, synth death/restart, buffer wraparound, full-buffer dropping, non-Latin-1 skipping, and TTY stop/start recovery. Lockdep and KCSAN are useful around concurrent producer and synth-thread consumption.
