# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_bns.c

## Purpose
Braille 'N Speak synthesizer driver using generic ttyio and generic Speakup output helpers.

## Important APIs, Types, And Functions
`synth_bns` sets name `bns`, init bytes, `spk_ttyio_ops`, generic tty probe/release/immediate, `spk_do_catch_up`, `spk_synth_flush`, and variables for caps, rate, pitch, volume, tone, direct, and timing.

## Control Flow
Module registration adds the synth. Probe attaches to selected tty; output and flush use shared paths.

## State And Persistence Behavior
Maintains tty pointer, alive flag, and runtime variable values in memory.

## Dependencies, Integration Points, Risks, And Test Signals
Depends on ttyio, shared synth thread/buffer, and sysfs variable handlers. Risks are tty configuration and device command compatibility. Test `ser`/`dev` probe, sysfs attributes, variable formatting, flush, unload/reload.
