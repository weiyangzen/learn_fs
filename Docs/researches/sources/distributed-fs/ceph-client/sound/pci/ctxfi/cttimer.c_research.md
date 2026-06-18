# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cttimer.c

## Purpose

This file provides per-PCM period notification timing for ctxfi using either Linux system timers or the native X-Fi interval timer IRQ.

## Important APIs, types, and functions

Public APIs are `ct_timer_new()`, `ct_timer_free()`, `ct_timer_instance_new()`, `ct_timer_instance_free()`, `ct_timer_prepare()`, `ct_timer_start()`, and `ct_timer_stop()`. Internal `struct ct_timer_instance` tracks one PCM stream; `struct ct_timer` manages global lists and native timer state. `ct_systimer_ops` implements per-stream `timer_list` scheduling. `ct_xfitimer_ops` multiplexes native timer IRQs across running streams.

## Control flow

`ct_timer_new()` selects native timer unless `use_system_timer` is set or hardware lacks timer IRQ support; native mode installs an IRQ callback in `struct hw`. Each PCM open creates an instance. System timer mode schedules the next callback from period size, current pointer, and sample rate. Native mode keeps a running list, reads hardware wallclock, computes the nearest fragment deadline, rearms the hardware timer, and calls `snd_pcm_period_elapsed()` outside the global timer lock when needed.

## State and persistence behavior

State includes per-instance running flags, last position, fragment countdown, need-update flag, and list membership. Global state includes instance/running lists, wallclock baseline, IRQ-handling/reprogram flags, and whether the hardware timer is running. State is in memory only, but native mode also persists timer enable/tick values in hardware registers.

## Dependencies and integration points

It depends on module parameter handling, ALSA PCM/core, `ctatc`, and `cthardware` timer callbacks. `ctpcm.c` creates one timer instance per substream and calls prepare/start/stop from PCM lifecycle paths.

## Risks and test signals

Risks include list races between IRQ and close, timer delete semantics in system mode, period calculation drift at unusual rates/formats, native timer reprogram races, and callbacks after `ct_timer_free()`. Tests should force both timer modes, run concurrent playback/capture streams, stress pause/resume/close, and verify stable period interrupts without XRUNs.
