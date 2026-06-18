# sources/distributed-fs/ceph-client/sound/usb/6fire/pcm.c

## Purpose
Implements 6Fire duplex PCM streaming over isochronous USB endpoints. Capture URB completions drive both capture ingestion and playback packet generation so output mirrors the incoming packet cadence.

## Important APIs, Types, and Functions
Public lifecycle functions are `usb6fire_pcm_init()`, `usb6fire_pcm_abort()`, and `usb6fire_pcm_destroy()`. ALSA PCM ops are open, close, prepare, trigger, and pointer. Important helpers include `usb6fire_pcm_set_rate()`, stream start/stop, capture/playback format copy functions, in/out URB handlers, URB initialization, and buffer allocation/destruction.

## Control Flow
Open assigns hardware constraints, limiting rates to the already selected runtime rate if streaming is active and setting max channels by direction. Prepare resets positions; if streaming is disabled, it maps ALSA rate to internal index, asks control code to stop streaming, set rate/altsetting/channel enables, restart hardware streaming, submits all input URBs, and waits for an output URB completion to confirm the stream is running. The input URB handler validates packet status, copies capture data into ALSA buffers, calculates matching output packet lengths, zero-fills playback packets, copies active playback data, stamps 6Fire packet headers/check bytes, submits output URB, then resubmits input URB. Trigger just toggles `pcm_substream.active`. Close deactivates substreams and stops USB streaming when both are closed.

## State and Persistence
`pcm_runtime` stores playback/capture substream state, panic flag, URB arrays and buffers, channel counts, packet sizes, stream mutex, stream state, rate index, wait queue, and startup condition. Per-substream state tracks active flag and DMA/period offsets. State is reset at stream stop and destroyed at card free.

## Dependencies and Integration Points
Depends on `control_runtime` to configure rate, altsetting, channel masks, and streaming bit; on USB ISO URBs; and on ALSA PCM vmalloc-managed buffers. Packet-size tables must match `firmware.c` endpoint descriptors and `control.c` altsettings.

## Risks
The in-URB handler calls `usb_submit_urb()` without checking return values for in/out resubmission. Any ISO packet status sets `panic`, after which PCM returns XRUN/EPIPE until reset by device lifecycle. Format handling uses pointer offset tricks for S24/S32 packing; alignment errors could corrupt samples. Stream start waits only one second for output running. Rate table synchronization across files is a recurring maintenance risk.

## Test Signals
Test playback-only, capture-only, and duplex streams at all six rates; S24_LE and S32_LE formats; period elapsed accounting across ring wrap; disconnect during active stream; ISO packet error forcing panic; and startup timeout/error paths.
