# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-audio-hook.c

## Purpose
`bttv-audio-hook.c` contains board-specific GPIO audio routing and volume helpers split out of `bttv-cards.c`. These routines adapt V4L2 tuner audio modes to the analog muxes, stereo/SAP pins, mute pins, and volume chip wiring found on older Bt848/Bt878 cards.

## Important APIs, Types, and Functions
Exported-by-header functions include `winview_volume()`, `gvbctv3pci_audio()`, `gvbctv5pci_audio()`, `avermedia_tvphone_audio()`, `avermedia_tv_stereo_audio()`, `lt9415_audio()`, `terratv_audio()`, `winfast2000_audio()`, `pvbt878p9b_audio()`, `fv2000s_audio()`, `windvr_audio()`, and `adtvk503_audio()`. They operate on `struct bttv`, `struct v4l2_tuner`, and the bttv GPIO helpers/macros from `bttvp.h`.

## Control Flow
Most audio hooks support a query path when `set` is false, filling `audmode` and `rxsubchans` with the modes the board may expose. When `set` is true, they switch on `t->audmode` and write board-specific GPIO masks using `gpio_bits()`, `gpio_inout()`, `gpio_read()`, `gpio_write()`, or `btaor()`. `winview_volume()` bit-bangs an 18-bit command sequence to a PT2254A volume chip with data, clock, and strobe pins.

## State and Persistence
The state is the board GPIO output latch and, for query calls, the caller-provided `v4l2_tuner` fields. Some routines suppress changes while `btv->radio_user` is active. No persistent configuration is stored by this file.

## Dependencies and Integration Points
The functions are referenced from `bttv_tvcards[]` entries through `.audio_mode_gpio` and `.volume_gpio`. They integrate with V4L2 tuner audio mode constants, global bttv GPIO debugging/tracking, and card definitions in `bttv-cards.c`.

## Risks and Edge Cases
The GPIO masks are card-specific and can mute audio or route the wrong source on board revisions with different wiring. Some comments explicitly note untested or variant-sensitive behavior, such as Prolink/FlyVideo stereo paths. Query paths often advertise broad capability because hardware status reporting is limited. GPIO writes must preserve unrelated pins through correct masks.

## Test Signals
Exercise mono/stereo/SAP/lang mode switching per supported card, verify no changes during radio-user paths where guarded, confirm GPIO tracking output matches expected masks, validate WinView volume bit-banging on a scope or known board, and check that audio remains unmuted after input changes.
