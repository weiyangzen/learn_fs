# sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp_input.c

## Purpose
Implements the input-subsystem beeper side of the PC speaker driver. It accepts `EV_SND` bell/tone events and programs PIT counter 2 directly unless PCM playback is active or beep output is muted.

## Important APIs, Types, And Functions
`pcspkr_do_sound()` performs the PIT and port `0x61` programming under `i8253_lock`. `pcspkr_stop_sound()` disables counter 2. `pcspkr_input_event()` validates sound events and converts tone frequency to PIT count. `pcspkr_input_init()` allocates/registers an input device with `SND_BELL` and `SND_TONE` capabilities.

## Control Flow
Platform probe calls `pcspkr_input_init()`. When userspace emits a bell or tone event, `pcspkr_input_event()` ignores it if PCM hrtimer playback is active or the mixer `pcspkr` flag is off. Bell events with nonzero value become 1000 Hz. Tone values between 20 and 32767 Hz are converted to PIT divisor counts; invalid or zero values stop sound. The low-level helper writes the PIT mode and divisor then enables/disables bits in port `0x61`.

## State And Persistence
The input device is devm-managed. Audible state is hardware PIT/speaker state plus `pcsp_chip.timer_active` and `pcsp_chip.pcspkr`; there is no persistence.

## Dependencies And Integration
Depends on Linux input APIs, ISA port I/O, global `pcsp_chip`, and `i8253_lock`. It integrates with mixer controls through `pcsp_chip.pcspkr` and with PCM playback through `timer_active` exclusion.

## Risks And Test Signals
Direct PIT programming can conflict with PCM playback if gating fails, hence the active-timer check is critical. Tests should cover bell/tone on/off, invalid event rejection, mute behavior, PCM-active suppression, suspend/shutdown stop, and input device registration metadata.
