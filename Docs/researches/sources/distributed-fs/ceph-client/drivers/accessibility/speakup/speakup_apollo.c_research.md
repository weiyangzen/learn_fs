# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_apollo.c

## Purpose
Apollo II synthesizer driver over ttyio with Apollo-specific command formats and catch-up behavior.

## Important APIs, Types, And Functions
`synth_apollo` uses name `apollo`, init `@R3@D0@K1\r`, `spk_ttyio_ops`, generic tty probe/release/immediate, custom `do_catch_up()`, and variables for caps, language, rate, pitch, voice, volume, direct, and timing.

## Control Flow
TTY probe attaches `N_SPEAKUP`. The custom catch-up loop drains the shared synth buffer, observes output backpressure, converts line endings/process-speech as needed, and sleeps based on delay/jiffy settings.

## State And Persistence Behavior
Maintains tty attachment, alive flag, and runtime variable values; no persistent storage.

## Dependencies, Integration Points, Risks, And Test Signals
Depends on ttyio, synth buffer/thread code, sysfs variable handlers, and module registration. Risks are Apollo command compatibility and tty write failures. Test probe, init/variable commands, language/voice params, catch-up under full output, and release.
