# sources/distributed-fs/ceph-client/sound/usb/line6/playback.h

## Purpose
`playback.h` is the Line 6 playback interface header. It declares the playback PCM operation table and the two output-URB management functions used by the Line 6 PCM core.

## Important APIs, Types, And Macros
The header exposes `snd_line6_playback_ops`, `line6_create_audio_out_urbs()`, and `line6_submit_audio_out_all_urbs()`. It includes ALSA PCM definitions and `driver.h` for `struct snd_line6_pcm`. `USE_CLEAR_BUFFER_WORKAROUND` enables a TonePort full-duplex monitor workaround that clears transfer buffers in the playback completion path.

## Control Flow And State
No runtime control flow is implemented here. The declarations allow the PCM setup code to install playback callbacks and create/submit output URBs. The workaround macro is compile-time state that changes the behavior of `audio_out_callback()` in `playback.c`.

## State And Persistence
There is no persistent state. The main state implication is the global compile-time workaround for output buffer clearing, motivated by TonePort jack full-duplex noise when software monitoring repeats stale output data.

## Dependencies And Integration Points
This header is consumed by Line 6 PCM and device drivers that need playback operations. It depends on ALSA PCM declarations and the Line 6 driver structures.

## Risks And Edge Cases
The workaround is broad: enabling it affects every playback URB completion compiled with this header, not only the TonePort scenario described in the comment. Changing it can alter software-monitor behavior and stale-buffer exposure.

## Test Signals
Build coverage should confirm all Line 6 playback users see the declarations. Runtime regression tests should focus on TonePort full-duplex monitoring with the workaround enabled and disabled, plus playback on devices that do not need software monitoring.
