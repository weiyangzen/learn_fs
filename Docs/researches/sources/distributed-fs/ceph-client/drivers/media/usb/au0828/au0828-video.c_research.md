# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/au0828-video.c

## Purpose
Implements AU0828 analog V4L2 video and VBI capture, including ISO URB management, packet parsing, buffer completion, video/VBI ioctls, tuner/input routing, media entities, suspend/resume, and video-device registration.

## Important APIs, types, and functions
ISO setup is handled by `au0828_init_isoc()` and `au0828_uninit_isoc()`, with `au0828_irq_callback()` resubmitting URBs. `au0828_isoc_copy()` parses AU0828 packet headers, separates VBI and video payload, handles field transitions, and fills active buffers via `au0828_copy_vbi()` and `au0828_copy_video()`. vb2 callbacks manage video buffers; VBI qops live in `au0828-vbi.c`. Stream control uses `au0828_start_analog_streaming()`, `au0828_stop_streaming()`, and `au0828_stop_vbi_streaming()`. V4L2 operations cover format, standard, input, audio, tuner, frequency, VBI format, selection, debug registers, status, and `DQBUF` green-screen recovery. Registration happens in `au0828_analog_register()`.

## Control flow and state
Open enables analog bridge streaming and resets hardware for the first user. `STREAMON` starts shared ISO URBs only for the first video/VBI streaming user, enables subdevice stream, and arms timeouts. URB completion parses packets under `slock`; new-field headers complete current buffers and fetch next queued buffers. Timeout handlers synthesize blank buffers so applications do not hang. Close may put tuner standby and set USB altsetting 0 when the last user exits. Format/standard/frequency changes initialize tuner through gated I2C and may interrupt active stream state.

## Dependencies and integration points
Depends on V4L2, vb2-vmalloc, V4L2 subdevices, media-controller source helpers, AU8522 analog ops, tuner ops, USB isochronous API, and AU0828 bridge registers.

## Risks and test signals
High-risk areas are packet parsing bounds, shared `streaming_users` across video/VBI, timeout buffer completion, suspend/resume URB state, green-screen reset heuristic, and media-source switching after input changes. Test signals include analog capture at UYVY 720x480, VBI capture, concurrent video+VBI, unplug during stream, input/frequency/standard ioctls, media graph source arbitration, blank-buffer timeout behavior, and no buffer overflows logged by copy helpers.
