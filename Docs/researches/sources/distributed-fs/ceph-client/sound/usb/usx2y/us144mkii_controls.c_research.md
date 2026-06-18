<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_controls.c -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_controls.c

## Purpose
Creates ALSA mixer controls for US-144MKII software routing and sample-rate reporting.

## APIs, Types, and Functions
Exports `tascam_create_controls()`. It defines enum info/get/put callbacks for line output source, digital output source, capture channels 1/2 source, capture channels 3/4 source, and a read-only integer `Sample Rate` control. Static `snd_kcontrol_new` objects define control names and callbacks.

## Control Flow, State, and Persistence
Routing get/put callbacks read or update `tascam_card` fields under `tascam->lock`. Playback routing selects whether line and digital outputs receive playback channels 1/2 or 3/4; capture routing selects analog or digital input pairs for ALSA capture channels. The sample-rate getter first returns cached `current_rate`; if unknown, it sends a UAC `GET_CUR` request to the audio-in endpoint and decodes the 24-bit little-endian frequency.

## Dependencies and Integration
Depends on ALSA control APIs, USB control transfers, and the routing helpers in `us144mkii_pcm.c` and capture/playback data paths that consume these state fields.

## Risks and Test Signals
Risks include controls changing while URB workers copy audio, sample-rate USB errors being ignored when fewer than three bytes are returned, default route asymmetry from probe initialization, and control names becoming ABI-visible. Test signals are `amixer` enumeration/get/put, live route switching, invalid enum rejection, sample-rate reads before and after stream configuration, and concurrent control updates during playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/us144mkii_controls.c -->
