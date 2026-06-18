# sources/distributed-fs/ceph-client/sound/hda/common/codec.c

## Purpose
Implements the common HD-audio codec core used by legacy HDA and ASoC HDA users. It wraps verb execution, caches codec topology and pin configuration, owns PCM/control/SPDIF helper creation, drives converter stream programming, handles runtime/system power transitions, and provides shared helpers for codec-specific patch drivers.

## Important APIs, Types, And Functions
Key exported entry points include `snd_hda_codec_device_init()`, `snd_hda_codec_device_new()`, `snd_hda_codec_new()`, `snd_hda_codec_register()`, `snd_hda_codec_unregister()`, `snd_hda_codec_cleanup_for_unbind()`, `snd_hda_codec_update_widgets()`, `snd_hda_codec_parse_pcms()`, `snd_hda_codec_build_pcms()`, `snd_hda_codec_build_controls()`, `snd_hda_codec_prepare()`, `snd_hda_codec_cleanup()`, `snd_hda_codec_setup_stream()`, `__snd_hda_codec_cleanup_stream()`, `snd_hda_add_new_ctls()`, `snd_hda_ctl_add()`, amp mixer callbacks, SPDIF control builders, multi-output helpers, pin-control helpers, GPIO setup, and `snd_hda_bus_reset_codecs()`. Internal state structures include cached connection lists, `hda_cvt_setup`, pin arrays, mixer/NID arrays, SPDIF arrays, and codec PCM lists.

## Control Flow
Codec creation initializes `struct hda_codec`, arrays, lists, delayed jack polling work, and the embedded `hdac_device`; device setup reads widget caps and pin defaults, powers the codec to D0, creates proc/hwdep endpoints, registers a component string, and optionally creates an ALSA managed device. PCM parsing asks the bound codec driver to build `hda_pcm` descriptions, fills default open/prepare/cleanup callbacks, assigns stable PCM device numbers, and delegates actual PCM creation to the controller side. Stream prepare programs converter stream/channel and format verbs, marks conflicting inactive converter setups dirty, then purges them under the bus prepare mutex. Suspend paths call codec driver suspend hooks, optionally clean streams, power widgets down, account power time, and may link down; resume restores power, pin controls, init verbs, jack state, and regmap cache.

## State And Persistence Behavior
The file maintains in-kernel caches for widget capabilities, initial/driver/user pin configurations, target pin controls, connection lists, converter stream setups, SPDIF status/control words, mixer ownership, PCM refcounts, and power accounting. Hardware state is persisted by cached regmap writes and by direct HDA verbs for pin, amp, converter, GPIO, SPDIF, and power state programming. PCM refs protect unbind until open streams drop references. Runtime PM state, delayed jack polling, and component strings are integrated into ALSA/device-core lifetime.

## Dependencies And Integration Points
Depends on ALSA core/control/PCM/TLV/jack APIs, `sound/hda_codec.h`, hdac regmap/bus helpers, runtime PM, `hda_local.h`, beep/jack/hwdep helpers, procfs support, and codec-driver ops from `struct hda_codec_driver`. It is called by controller probing and codec-specific patch drivers, and it calls back into controller attachment through `snd_hda_attach_pcm_stream()`.

## Risks And Test Signals
Risks concentrate around hardware communication fallback, cache coherency after reconfiguration, converter stream reuse, PM ordering, jack polling during suspend, SPDIF index assignment, and control-name collision handling. Useful test signals are HDA probe logs, `/proc/asound/card*/codec#*`, hwdep verb access, mixer control enumeration, PCM open/prepare/trigger playback and capture, runtime suspend/resume cycles, hot-unbind/rebind, jack polling, SPDIF status changes, and codec-specific regression tests.
