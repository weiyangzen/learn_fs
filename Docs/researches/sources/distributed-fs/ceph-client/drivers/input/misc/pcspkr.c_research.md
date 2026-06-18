# sources/distributed-fs/ceph-client/drivers/input/misc/pcspkr.c

Purpose: legacy PC speaker input driver supporting EV_SND bell and tone playback.

Important APIs/types/functions: platform driver, input EV_SND, PIT constants, I/O port access, and `i8253_lock`. Main routines are `pcspkr_event`, probe, remove, suspend, and shutdown.

Control flow: probe allocates/registers an ISA-identified input device with SND_BELL/SND_TONE. Events validate type/code, map nonzero bell to 1000 Hz, compute PIT count for tones in range, lock `i8253_lock`, program PIT counter 2 and port `0x61` to enable sound or clear bits to stop it. Remove/suspend/shutdown stop sound.

State/persistence: no driver-persistent state; hardware PIT/speaker gate is turned off on lifecycle stops or zero events.

Dependencies/integration: platform `pcspkr`, PIT/ISA speaker ports, input sound events.

Risks: direct I/O is platform-sensitive. Out-of-range tones stop output. No restoration after suspend and no coordination beyond i8253 lock.

Test signals: bell, tone, zero stop, invalid events, suspend/remove/shutdown stop, and platform binding.
