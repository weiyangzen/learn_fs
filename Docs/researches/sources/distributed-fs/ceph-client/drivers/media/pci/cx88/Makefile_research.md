# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/Makefile

## Purpose
Builds the cx88 driver modules and maps Kconfig symbols to their object files. It keeps the common cx88 core separate from analog video, cx8802 MPEG transport, ALSA audio, Blackbird MPEG encoder, DVB, and optional VP3054 I2C glue.

## Important APIs, Types, And Data
The make variables define module composition: `cx88xx-objs` contains `cx88-cards.o`, `cx88-core.o`, `cx88-i2c.o`, `cx88-tvaudio.o`, `cx88-dsp.o`, and `cx88-input.o`; `cx8800-objs` contains analog video and VBI; `cx8802-objs` contains MPEG transport support. Conditional `obj-$(CONFIG_...)` lines build `cx88xx.o`, `cx8800.o`, `cx8802.o`, `cx88-alsa.o`, `cx88-blackbird.o`, `cx88-dvb.o`, and `cx88-vp3054-i2c.o`.

## Control Flow
There is no runtime flow; build flow follows the kernel kbuild rules. Base cx88 always links common code and analog capture when `CONFIG_VIDEO_CX88` is enabled. The cx8802 transport module appears only when `CONFIG_VIDEO_CX88_MPEG` is set by DVB or Blackbird. ALSA, Blackbird, DVB, and VP3054 compile independently as optional modules that bind to shared exported symbols from `cx88xx` and `cx8802`.

## State And Persistence
The file contributes only build artifacts. Persistent effects are generated `.o` and `.ko` files and module dependency metadata. There is no runtime state.

## Dependencies And Integration Points
The Makefile relies on Kconfig to provide valid symbol combinations. It adds include paths for `drivers/media/tuners` and `drivers/media/dvb-frontends`, which are needed by cx88 board, tuner, and DVB attach code. The object grouping reflects integration contracts: card/core/I2C/audio/input helpers live in the common module, while video, MPEG transport, ALSA, Blackbird, and DVB are separable front ends over shared hardware.

## Risks And Test Signals
Risks are missing objects when new symbols are exported, stale include paths if media frontend layout changes, and accidental module split changes that break symbol resolution. Test signals are kernel builds for every Kconfig combination, `modpost` symbol checks, and module dependency inspection showing optional modules depending on `cx88xx` and, for DVB/Blackbird, `cx8802`.
