# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/thread.c

## Purpose
`thread.c` implements the Speakup progression kthread. It waits for speech-buffer work, flush requests, and pending beeps, then drives synthesizer catch-up and restarts TTY output processing.

## Important APIs, Types, And Functions
It exports `DECLARE_WAIT_QUEUE_HEAD(speakup_event)` and defines `speakup_thread(void *data)`. The loop uses `struct bleep`, `spk_unprocessed_sound`, `kd_mksound()`, `synth`, `synth->catch_up`, `synth_buffer_empty()`, `speakup_info.flushing`, and `speakup_start_ttys()`.

## Control Flow
The thread starts with `spk_mutex` held and loops until `kthread_should_stop()`. It prepares a wait entry, takes `speakup_info.spinlock`, copies and clears `spk_unprocessed_sound`, and decides whether to break out for stop, sound playback, or synth catch-up work. If no work is ready, it drops `spk_mutex`, schedules, and reacquires the mutex. After wakeup it finishes the wait, plays any pending sound via `kd_mksound()`, invokes `synth->catch_up(synth)` when the active synth is alive and has buffered or flushing work, and then calls `speakup_start_ttys()`.

## State And Persistence
The thread itself persists as a kernel task while Speakup is running. It consumes the one-shot `spk_unprocessed_sound` state by clearing `active` under the Speakup spinlock. It does not persist data outside memory.

## Dependencies And Integration Points
It depends on kernel kthreads and wait queues plus Speakup internals declared in `spk_types.h`, `speakup.h`, and `spk_priv.h`. It is woken by `synth_start()`, `spk_do_flush()`, synth timers, and other Speakup paths that signal `speakup_event`.

## Risks
The file deliberately calls `synth->catch_up()` without holding `speakup_info.spinlock`, so the callee must perform its own locking and be robust against sleeping. Correct lock ordering between `spk_mutex` and the spinlock is important. Missed wakeups or incorrect `prepare_to_wait()`/`finish_wait()` use would stall speech output or beeps.

## Test Signals
Regression coverage should include queued speech wakeups, flush wakeups, beep delivery, `kthread_stop()` shutdown, and TTY restart after catch-up. Stress tests should combine high-rate output with synth removal or state changes.
