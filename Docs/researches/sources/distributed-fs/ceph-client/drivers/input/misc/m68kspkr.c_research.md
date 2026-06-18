# sources/distributed-fs/ceph-client/drivers/input/misc/m68kspkr.c

Purpose: exposes m68k low-level `mach_beep` as an EV_SND input device supporting bell and tone.

Important APIs/types/functions: platform driver/device registration, input sound events, and architecture `mach_beep`. Main routines are `m68kspkr_event`, probe, remove, shutdown, module init, and exit.

Control flow: module init refuses load without `mach_beep`, registers a platform driver, creates a synthetic platform device, and lets probe allocate/register an input device. Events map nonzero SND_BELL to 1000 Hz or SND_TONE to a divisor count when in range, then call `mach_beep(count, -1)`. Remove/shutdown stop sound.

State/persistence: no durable state; only input/platform device lifecycle and current hardware beep state.

Dependencies/integration: m68k architecture beep hook and input EV_SND.

Risks: returns `-1` rather than `-EINVAL` for invalid events. Fallthrough from SND_BELL to SND_TONE is intentional but unannotated. Hardware locking is delegated to `mach_beep`.

Test signals: load with/without `mach_beep`, SND_BELL/SND_TONE, invalid events, and stop on remove/shutdown.
