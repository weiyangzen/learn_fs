# sources/distributed-fs/ceph-client/sound/usb/caiaq/audio.c

## Purpose
Implements CAIAQ PCM audio over isochronous USB endpoints for multiple Native Instruments devices. It supports paired stereo streams, device-specific sample alignment modes, and duplex operation where capture completions generate matching playback URBs.

## Important APIs, Types, and Functions
Public functions are `snd_usb_caiaq_audio_init()`, `snd_usb_caiaq_audio_disconnect()`, and `snd_usb_caiaq_audio_free()`. ALSA PCM ops include open, close, hw_free, prepare, trigger, and pointer. Key helpers include `stream_start()`, `stream_stop()`, `activate_substream()`, `deactivate_substream()`, `read_in_urb_mode0/2/3()`, `fill_out_urb_mode_0/3()`, `read_completed()`, `write_completed()`, `alloc_urbs()`, and `free_urbs()`.

## Control Flow
Initialization derives audio stream counts from device spec, creates an ALSA PCM with one substream per stereo stream, sets supported rates by product id, allocates callback info plus 32 input and 32 output ISO URBs, and registers PCM ops. Prepare sets per-stream buffer offsets according to `spec.data_alignment`; if streaming is not active, it locks sample rate for all active streams, computes bytes-per-packet, sends audio params over EP1, starts streaming by submitting all input URBs, and waits for the first output completion. Input URB completion finds a free output URB bit, mirrors input frame lengths into output frames, under spinlock fills playback data and reads capture data, reports elapsed periods, submits output URB if data was present, and resubmits input URB. Write completion marks output running and clears the active bit.

## State and Persistence
State is stored in `snd_usb_caiaqdev`: stream counts, streaming flags, per-stream buffer/period positions, panic flags, audio buffers, samplerate mask, bytes-per-packet, out URB active bitmask, substream arrays, PCM handle, URB arrays, and callback info. It persists until card free; disconnect stops streaming but final memory cleanup happens in `audio_free()`.

## Dependencies and Integration Points
Depends on `device.c` command helpers for setting audio params and on CAIAQ device spec received via EP1. Integrates with ALSA PCM vmalloc buffers and USB ISO endpoints 2 capture / 6 playback.

## Risks
Read completion uses `urb->iso_frame_desc[outframe].actual_length` when assigning output length while iterating `frame`; review suggests it likely meant the current input frame, so nonmatching skipped frames may be risky. URB submit return values in completion paths are mostly ignored. Stream position arrays are indexed by substream number and require `n_streams <= MAX_STREAMS`. Alignment modes are protocol-sensitive and panic on check-byte mismatch. Closing checks substream arrays before `hw_free()` may leave stream running until `hw_free()` deactivates.

## Test Signals
Test all supported sample rates per product, data alignment modes 0/2/3, multiple stereo stream counts, playback/capture period elapsed behavior, ISO frame status errors, output URB exhaustion, disconnect while streaming, and audio-param timeout/failure.
