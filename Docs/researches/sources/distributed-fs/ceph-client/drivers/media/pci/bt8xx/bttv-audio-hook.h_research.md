# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-audio-hook.h

## Purpose
`bttv-audio-hook.h` declares the board-specific audio GPIO hook functions used by the bttv card table.

## Important APIs, Types, and Functions
The header includes `bttvp.h` and declares the volume hook `winview_volume()` plus audio mode hooks for Lifetec, AVerMedia, TerraTV, I-O Data GV-BCTV, WinFast, Prolink/FlyVideo, WinDVR, and AD-TVK503 boards. Each audio hook accepts `struct bttv *`, `struct v4l2_tuner *`, and a `set` flag.

## Control Flow
There is no executable control flow. The declarations allow `bttv-cards.c` to assign function pointers in `struct tvcard` initializers and call sites to compile with type checking.

## State and Persistence
The header declares functions that manipulate volatile GPIO state, but it stores no state itself.

## Dependencies and Integration Points
It binds `bttv-audio-hook.c` to `bttv-cards.c` and depends on the private bttv structures and V4L2 tuner definitions made available by `bttvp.h`.

## Risks and Edge Cases
Prototype drift between the header and implementation would break function-pointer assignment or calls. Because this is private driver API, changes must be synchronized with card table fields such as `.audio_mode_gpio` and `.volume_gpio`.

## Test Signals
Build coverage is the primary signal: all card table assignments compile, hooks link into `bttv.o`, and no incompatible pointer type warnings are emitted.
