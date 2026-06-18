# sources/distributed-fs/ceph-client/sound/usb/endpoint.c

## Purpose
Provides the generic USB-audio endpoint streaming engine. It abstracts isochronous data and feedback endpoints, manages interface and clock refcounts, allocates URBs, calculates packet sizes, starts/stops streams, handles completion callbacks, and connects endpoint traffic to ALSA PCM data callbacks.

## Important APIs and Types
Public APIs include `snd_usb_add_endpoint()`, `snd_usb_get_endpoint()`, `snd_usb_endpoint_open()`, `snd_usb_endpoint_close()`, `snd_usb_endpoint_set_params()`, `snd_usb_endpoint_prepare()`, `snd_usb_endpoint_start()`, `snd_usb_endpoint_stop()`, `snd_usb_endpoint_release()`, `snd_usb_endpoint_free_all()`, `snd_usb_endpoint_set_sync()`, `snd_usb_endpoint_set_callback()`, `snd_usb_endpoint_get_clock_rate()`, `snd_usb_endpoint_next_packet_size()`, and `snd_usb_queue_pending_output_urbs()`. Private `snd_usb_iface_ref` and `snd_usb_clock_ref` objects serialize shared USB interface altsetting and shared clock rate use.

## Control Flow
Endpoint creation adds a data or sync endpoint to `chip->ep_list` and computes the pipe from endpoint direction. `snd_usb_endpoint_open()` is called from hw_params, records interface/altsetting/rate/format/period constraints on first open, verifies compatibility on later opens, and increments interface and clock open counts. `snd_usb_endpoint_set_params()` releases old URBs, computes nominal frequency, packets per second, small/large packet sizes, max frame sizes, and delegates to data or sync URB allocation. `snd_usb_endpoint_prepare()` deselects/selects interfaces, applies mode/pitch/rate setup, handles UAC1-vs-UAC2 order quirks, and clears setup flags. `snd_usb_endpoint_start()` increments running refs, locks clock rate, initializes accumulators, submits URBs or queues ready playback URBs for implicit feedback. Completion callbacks retire data, process sync feedback, prepare the next URB, and resubmit until stopped. Stop moves state from running to stopping, unlinks active URBs unless pending URBs are intentionally kept, and `wait_clear_urbs()` finalizes cleanup.

## State and Persistence
State is volatile and spread across atomics (`running`, `state`, `submitted_urbs`), bitmasks (`active_mask`, `unlink_mask`), packet FIFOs for implicit feedback, USB interface `altset`, clock `rate/locked/need_setup`, and endpoint flags `need_setup`/`need_prepare`. Device-visible state includes interface altsettings and sample rates programmed through `clock.c`; no disk persistence exists.

## Dependencies and Integration
Depends on ALSA PCM params, Linux USB URB APIs, `clock.c`, `helper.c`, PCM callbacks from `pcm.h`, and quirk hooks such as `snd_usb_select_mode_quirk()`, `snd_usb_init_pitch()`, and `snd_usb_endpoint_start_quirk()`. It is the runtime bridge between parsed `audioformat` objects and PCM data movement.

## Risks and Test Signals
Risks include races across completion callbacks and stop, refcount imbalance between open/start/stop/close, clock-rate conflicts on shared clocks, URB leaks after partial allocation, implicit-feedback FIFO overflow, bad packet-size math for high-speed intervals, and quirks that require nonstandard interface ordering. Test signals include playback/capture start-stop loops, low-latency playback, implicit feedback devices, sync endpoint feedback format detection, suspend/resume, disconnect while active, and KASAN/lockdep coverage for URB cleanup.
