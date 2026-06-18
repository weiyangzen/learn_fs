# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/synth.c

## Purpose
`synth.c` is the central Speakup speech-synthesizer manager. It owns the active global `struct spk_synth *synth`, the registered synthesizer list, the shared `speakup_info` spinlock state, synth output buffering, UTF-8-to-wide-character ingress helpers, catch-up output flow control, synth index commands, I/O port resource claims, and synth attach/release paths.

## Important APIs, Types, And Functions
The exported state and APIs include `speakup_info`, `spk_do_catch_up`, `spk_do_catch_up_unicode`, `spk_synth_flush`, `spk_synth_get_index`, `spk_synth_is_alive_nop`, `spk_synth_is_alive_restart`, `synth_printf`, `synth_putwc`, `synth_putwc_s`, `synth_putws`, `synth_putws_s`, `synth_request_region`, `synth_release_region`, `synth_add`, `synth_remove`, and `synth_current`. `synth_time_vars` provides default Speakup timing variables for delay, trigger, jiffy delta, full timeout, and flush timeout. Internal control is concentrated in `_spk_do_catch_up()`, `synth_start()`, `spk_do_flush()`, `synth_utf8_get()`, `synth_writeu()`, `do_synth_init()`, and `synth_release()`.

## Control Flow
Text enters through `synth_write()`, `synth_writeu()`, `synth_printf()`, or wide-character helpers, is appended to the synth buffer, and `synth_start()` arms `thread_timer` based on the `TRIGGER` variable. The Speakup thread wakes on `speakup_event` and calls the synth's `catch_up` callback, normally `spk_do_catch_up()` or the Unicode variant. `_spk_do_catch_up()` repeatedly locks `speakup_info.spinlock`, handles flush requests, skips non-Latin-1 when needed, peeks the next buffered character, sleeps if the synth reports full, periodically emits the synth `procspeech` marker at spaces, and consumes characters only after output succeeds. Initialization looks up a named synth from `synths`, releases any existing synth, probes the new one, copies timing defaults from the synth descriptor, emits the init string, registers variables, creates optional sysfs attributes, and wakes the Speakup thread. Removal reverses that by stopping output, deleting the timer, removing sysfs, unregistering variables, and invoking the synth release callback.

## State And Persistence
All state is in kernel memory. Persistent user-visible effects are through sysfs groups created by individual synth drivers and through registered Speakup variables. Shared mutable state includes `synth`, `synths`, `spk_pitch_buff`, `spk_quiet_boot`, `speakup_info.flushing`, `thread_timer`, `index_count`, `sentence_count`, and `synth_res`. Buffer and timing updates are protected by `speakup_info.spinlock`; synth registration and selection are serialized by `spk_mutex`.

## Dependencies And Integration Points
The file depends on Speakup private headers (`spk_priv.h`, `speakup.h`, `serialio.h`), the synth buffer helpers, kernel timers, wait queues, kthreads, sysfs, ioport resources, and per-synth `io_ops`. It integrates with `thread.c` through `speakup_event` and `speakup_task`, with variable registration in `varhandlers.c`, with serial synth drivers through `struct spk_synth`, and with console/keyboard paths that enqueue Speakup output.

## Risks
This file is concurrency-sensitive: lock handoff in `_spk_do_catch_up()`, timer wakeups, flush handling, and synth release must avoid sleeping while holding the Speakup spinlock or dereferencing a released synth. `synth_utf8_get()` accepts 2- through 6-byte forms and only stores values below `0x10000`, so malformed or supplementary-plane input is dropped rather than fully represented. `synth_release_region()` ignores its arguments and releases the single static `synth_res`, so callers must not assume independent ranges. Indexing functions assume `synth` and `synth->get_index` are valid when called.

## Test Signals
Useful signals are boot/module tests selecting and releasing synth drivers, sysfs variable registration and removal, Speakup text output under flush and full-buffer conditions, Unicode and invalid UTF-8 output, and synth index count progression. Race-oriented tests should exercise synth removal while `speakup_thread()` is active, timer-triggered catch-up, and pitch-shift restoration in `spk_do_flush()`.
