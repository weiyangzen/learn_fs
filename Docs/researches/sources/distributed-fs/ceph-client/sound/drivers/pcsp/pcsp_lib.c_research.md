# sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp_lib.c

## Purpose
Implements the PCM playback engine for the PC speaker driver. It converts mono PCM sample bytes into PIT counter 2 pulses using an hrtimer, advances ALSA buffer pointers, and reports period elapsed through a workqueue.

## Important APIs, Types, And Functions
Exports `pcsp_do_timer()`, `pcsp_sync_stop()`, and `snd_pcsp_new_pcm()`. Internal helpers include `pcsp_timer_update()`, `pcsp_pointer_update()`, `pcsp_start_playing()`, `pcsp_stop_playing()`, and PCM callbacks for open/close/hw_params/hw_free/prepare/trigger/pointer. Module parameter `nforce_wa` changes PIT programming for an NForce chipset workaround.

## Control Flow
PCM open rejects active playback, sets runtime hardware constraints, and records the substream. Prepare stops any existing timer, resets pointers, and records sample size/sign. Trigger start programs PIT mode, stores port `0x61` state, marks timer active, and starts the hrtimer. Each timer callback writes a pulse width derived from the current sample, optionally handles the NForce half-cycle workaround, updates playback and period pointers, queues `snd_pcm_period_elapsed()` on `system_highpri_wq`, and rearms itself. Stop clears `timer_active` and restores PIT mode/port bits. Sync stop cancels the hrtimer and pending work.

## State And Persistence
State is in global `pcsp_chip`: playback substream pointer, format size/sign, playback/period pointers, timer-active flag, half-cycle state, nanosecond remainder, and saved port value. There is no persistence.

## Dependencies And Integration
Depends on ALSA PCM helpers, hrtimers, workqueues, PIT `i8253_lock`, raw I/O ports, and shared constants/state from `pcsp.h`. Mixer controls can toggle `chip->enable`, affecting whether pulses are emitted.

## Risks And Test Signals
The callback path touches hardware from hrtimer context and defers ALSA period notifications to avoid long IRQ work. Pointer math assumes mono and fixed rate constraints. Tests should cover start/stop races, close/hw_free synchronization, S16 and U8 formats, period elapsed timing, pointer wraparound, `nforce_wa`, mixer enable gating, and suppression of input beeps while PCM is active.
