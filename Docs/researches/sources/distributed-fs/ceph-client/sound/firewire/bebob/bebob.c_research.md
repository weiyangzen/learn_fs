# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob.c

Purpose: provides the BeBoB driver entry point, FireWire ID matching, ALSA card allocation, device naming, vendor/model spec selection, probe/remove/update handling, and module registration.

Important APIs/functions: `bebob_probe`, `bebob_update`, `bebob_remove`, `bebob_card_free`, `name_device`, `detect_quirks`, `get_saffire_spec`, `check_audiophile_booted`, `snd_bebob_init`, and `snd_bebob_exit`. It also declares module parameters `index`, `id`, and `enable`, and a large `ieee1394_device_id` table mapping vendor/model pairs to `snd_bebob_spec`.

Control flow and state: probe chooses a spec from ID data, Focusrite Saffire name probing, or M-Audio bootloader checks. It allocates an ALSA card, stores `struct snd_bebob`, names the card from CSR/register data, detects quirks, discovers streams, initializes duplex streaming, creates proc/MIDI/PCM/hwdep interfaces, and registers the card. Remove blocks until ALSA character devices close through `snd_card_free`. Bus update only refreshes FCP state, intentionally avoiding stream update because BeBoB bus resets cause packet discontinuity expected to surface as XRUN.

Dependencies/integration: integrates FireWire core driver registration, ALSA card lifecycle, BeBoB stream/PCM/MIDI/hwdep helpers, FCP, and M-Audio firmware loading. Risks include device table specificity, bootloader/spec misclassification, card index bitmap cleanup, and the M-Audio scheduled bus reset workaround. Test signals include matching known devices, successful card registration, correct longname/GUID, firmware cue behavior, and XRUN/reprepare behavior across bus resets.
