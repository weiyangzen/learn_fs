# sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp_input.h

## Purpose
Declares the small public interface between PC speaker platform setup and the input beeper implementation.

## Important APIs, Types, And Functions
Declares `pcspkr_input_init(struct input_dev **rdev, struct device *dev)` and `pcspkr_stop_sound(void)`.

## Control Flow
No executable flow exists. `pcsp.c` calls `pcspkr_input_init()` during platform probe and `pcspkr_stop_sound()` during shutdown/suspend/free paths.

## State And Persistence
No state is defined. State is owned by `pcsp_input.c` and the shared `pcsp_chip`.

## Dependencies And Integration
Relies on forward-visible `struct input_dev` and `struct device` declarations from includers. It is the boundary that lets `pcsp.c` stop beeps without knowing PIT programming details.

## Risks And Test Signals
Prototype drift would break the PC speaker module build. Build tests and suspend/shutdown smoke tests are the main signals.
