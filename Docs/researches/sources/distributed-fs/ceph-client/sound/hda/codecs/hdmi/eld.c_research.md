# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/eld.c

## Purpose
Provides generic HDMI ELD retrieval, procfs display/update helpers, and PCM capability narrowing based on parsed ELD/SAD data for HDA HDMI codecs.

## Important APIs, Types, and Functions
`snd_hdmi_get_eld_size()` reads the HDA HDMI DIP ELD buffer size. `snd_hdmi_get_eld()` reads every byte with `AC_VERB_GET_HDMI_ELDD`, validates the ELD valid bit, checks for empty first-byte data, handles a zero-size ASUS workaround by forcing 128 bytes, and returns the filled buffer and size. Under `CONFIG_SND_PROC_FS`, `snd_hdmi_print_eld_info()` prints monitor state, pin/device/converter NIDs, and parsed ELD details, while `snd_hdmi_write_eld_info()` lets procfs input mutate selected monitor, connection, speaker, and SAD fields for debugging/testing. `snd_hdmi_eld_update_pcm_info()` intersects a PCM stream's rates, formats, max bits per sample, and channel maximum with sink capabilities from parsed SAD entries.

## Control Flow
ELD retrieval first asks the codec for the DIP ELD buffer size, validates it against fixed and maximum ELD sizes, then loops through bytes. If the graphics driver is concurrently updating ELD and the valid bit drops, or if byte zero is zero, retrieval aborts with `-EINVAL` so callers can repoll. On success, the caller receives the exact ELD size. Procfs print exits early when ELD is invalid; write scans `name value` lines and updates only allowed parsed fields, including numbered `sadN_*` attributes. PCM update starts from mandatory basic audio stereo support, folds in all SAD rates/channels/LPCM bit depths, then restricts the codec stream descriptor to the sink-supported subset.

## State and Persistence Behavior
The file mostly operates on caller-owned `struct hdmi_eld`, `struct snd_parsed_hdmi_eld`, and `struct hda_pcm_stream` objects. `snd_hdmi_write_eld_info()` mutates in-memory ELD/debug state exposed by procfs but does not write sink EDID or hardware ELD registers. `snd_hdmi_eld_update_pcm_info()` destructively narrows the supplied PCM stream fields, so callers must start from codec capabilities before applying sink restrictions.

## Dependencies and Integration Points
It depends on the HDA codec verb interface, ALSA HDMI ELD parser/types, CEA SAD constants, procfs info buffers when enabled, and `hda_local.h`. It is linked into the generic HDMI codec object by the HDMI Makefile and is used by HDMI codec implementations when monitor ELD changes or when user space inspects HDMI sink information.

## Risks
ELD can be transient while the graphics driver updates it, so callers must handle `-EINVAL` and retry rather than treating it as permanent absence. The zero-size workaround assumes 128 bytes and may mask firmware/controller defects. Procfs write support is powerful for testing but can create in-memory sink capabilities that do not match real hardware. PCM narrowing can over-restrict streams if applied repeatedly without resetting to base codec capabilities first.

## Test Signals
Tests should cover normal ELD reads, invalid-valid-bit repoll behavior, zero-size workaround, invalid size rejection, DVI/zero-first-byte handling, procfs print/write round trips for SAD fields, LPCM 20/24-bit promotion to S32_LE, channel/rate restriction from SAD data, and HDMI hotplug flows where ELD changes update PCM capabilities without stale limits.
