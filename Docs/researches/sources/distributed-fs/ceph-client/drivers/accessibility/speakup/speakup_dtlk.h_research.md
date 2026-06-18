# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dtlk.h

## Purpose
Private DoubleTalk PC hardware constants and interrogation response layout.

## Important APIs, Types, And Functions
Defines `SYNTH_IO_EXTENT`, `SYNTH_CLEAR`, status bits such as `TTS_READABLE`, `TTS_WRITABLE`, and `TTS_ALMOST_FULL`, plus `struct synth_settings` for serial number, ROM version, mode, punctuation, pitch/speed/volume/tone, memory, and other firmware fields.

## Control Flow
No executable code; consumed by `speakup_dtlk.c`.

## State And Persistence Behavior
No state is stored. The struct defines local/static parse results in the driver.

## Dependencies, Integration Points, Risks, And Test Signals
Tightly coupled to DoubleTalk firmware response bytes. Wrong bits or field order break readiness and interrogation. Test against known hardware responses and readable/writable/almost-full transitions.
