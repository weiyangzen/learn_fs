# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_decext.c

## Purpose
DECtalk External ttyio driver with DEC-specific command strings, XON/XOFF fullness detection, and escape-aware process-speech handling.

## Important APIs, Types, And Functions
`synth_decext` uses name `decext`, `SF_DEC`, ttyio, `read_buff_add()`, custom `do_catch_up()`, and `synth_flush()`. Variables include caps, rate, pitch, inflection, volume, punctuation, voice, direct, and timing.

## Control Flow
Receive callback records the last byte; `synth_full()` treats XOFF as full. Catch-up skips non-Latin-1, waits on fullness/output failure, tracks `[`/`]` escape state, converts newline, and emits process-speech after punctuation or jiffy intervals when safe. Flush clears state and sends a DEC clear sequence.

## State And Persistence Behavior
State includes volatile last received byte, `in_escape`, tty pointer, alive flag, and variables.

## Dependencies, Integration Points, Risks, And Test Signals
Depends on ttyio receive callbacks, synth buffer helpers, and DEC spacing behavior in core output. Risks are missed flow-control transitions and injecting process-speech into command sequences. Test XON/XOFF, flush in escape state, punctuation pacing, variable ranges, and release.
