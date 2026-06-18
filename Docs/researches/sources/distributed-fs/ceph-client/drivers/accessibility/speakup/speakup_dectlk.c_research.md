# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dectlk.c

## Purpose
DECtalk Express ttyio driver with DEC command formatting, flush acknowledgement handling, XON/XOFF support, and read-all indexing.

## Important APIs, Types, And Functions
`synth_dectlk` registers name `dectlk`, `SF_DEC`, ttyio, `read_buff_add()`, `get_index()`, custom `do_catch_up()`, `synth_flush()`, `flush_time`, and indexing command `[:in re %d ]`. It also provides per-voice default pitch/volume arrays.

## Control Flow
Receive callback handles control-A flush completion, XOFF/XON fullness, numeric index accumulation, and last-index publication. Catch-up waits for flush completion or timeout, drains buffered text with escape tracking, and emits process-speech safely. Flush closes any open escape, marks flushing, flushes tty, and sends clear.

## State And Persistence Behavior
State includes `xoff`, `in_escape`, `is_flushing`, wait queue, `lastind`, tty pointer, alive flag, voice defaults, and variables.

## Dependencies, Integration Points, Risks, And Test Signals
Integrates with ttyio receive flow, core read-all indexing, and voice-default reset in `spk_var_store()`. Risks are lost flush acks, malformed index parsing, and escape-state errors. Test XON/XOFF, flush timeout, read-all index feedback, voice default resets, and sysfs `flush_time`.
