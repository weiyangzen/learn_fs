# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_dummy.c

## Purpose
Dummy tty-backed synth driver for smoke-testing Speakup without a real hardware protocol.

## Important APIs, Types, And Functions
`synth_dummy` registers name `dummy`, init string `Speakup\n`, ttyio transport, `spk_do_catch_up_unicode`, generic flush, restart liveness, and a simple `read_buff_add()`. Variables include caps, rate, pitch, inflection, volume, tone, punctuation, direct, and timing.

## Control Flow
Probe delegates to ttyio. Unicode-capable generic catch-up drains Speakup output through ttyio. Sysfs variables emit simple command strings.

## State And Persistence Behavior
Maintains tty pointer, alive flag, receive behavior, and variable values only while loaded.

## Dependencies, Integration Points, Risks, And Test Signals
Depends on ttyio and generic unicode synth paths. It may not expose hardware timing bugs. Test synth selection, ttyio open/release, Unicode output, sysfs variables, and no-hardware operation.
