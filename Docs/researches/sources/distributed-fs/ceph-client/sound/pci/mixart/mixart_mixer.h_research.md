# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_mixer.h

## Purpose
This small header declares the mixer interface exported by `mixart_mixer.c` to the rest of the miXart driver.

## Important APIs, types, and functions
It declares `mixart_update_playback_stream_level`, `mixart_update_capture_stream_level`, and `snd_mixart_create_mixer`. The first two are used by PCM hardware-parameter setup to push cached stream levels once stream format/buffer setup occurs. The third creates ALSA controls and initializes hardware-visible levels after firmware setup.

## Control flow
The header has no runtime control flow. It enables `mixart.c` and `mixart_hwdep.c` to call mixer routines without depending on mixer implementation details.

## State and persistence behavior
No state is stored here. The declarations operate on `struct snd_mixart` and `struct mixart_mgr` state defined in `mixart.h`.

## Dependencies and integration points
The prototypes require the driver-visible `struct snd_mixart` and `struct mixart_mgr` declarations from `mixart.h` in including translation units. It is included by `mixart.c`, `mixart_hwdep.c`, and `mixart_mixer.c`.

## Risks and edge cases
Signature drift between this header and the implementation would break the module build. Because these functions are cross-file integration points, changes to mixer locking or pipe assumptions need coordinated updates in PCM and firmware setup code.

## Test signals
Successful `snd-mixart` build is the direct signal. Runtime signals are covered by PCM `hw_params` stream-level updates and mixer creation after firmware setup.
