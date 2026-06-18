<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_kctl.c -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_kctl.c

## Purpose
Dynamic ALSA mixer-control bridge for virtio-snd. It parses virtio control metadata, creates ALSA kcontrols, translates get/put/TLV operations into virtio control messages, and dispatches control-change events.

## APIs, Types, and Functions
Exports `virtsnd_kctl_parse_cfg()`, `virtsnd_kctl_build_devs()`, and `virtsnd_kctl_event()`. Static maps translate virtio types, access flags, and event masks to ALSA values. Important callbacks are `virtsnd_kctl_info()`, `virtsnd_kctl_get()`, `virtsnd_kctl_put()`, `virtsnd_kctl_tlv_op()`, and `virtsnd_kctl_get_enum_items()`.

## Control Flow, State, and Persistence
Parse runs only when the controls feature is negotiated, reads the control count, allocates metadata and runtime arrays, queries `VIRTIO_SND_R_CTL_INFO`, and for enumerated controls queries item strings. Build constructs `snd_kcontrol_new` records from virtio names, indices, access masks, TLV flags, callbacks, and private control IDs, then adds them to the ALSA card. Get/put allocate virtio messages, convert values by type/endian, and synchronously send read/write requests. TLV read/write/command uses separate user-copy buffers and scatterlists. Events translate virtio masks and notify ALSA for the affected control ID.

## Dependencies and Integration
Depends on ALSA control APIs, virtio control-message transport, virtio-snd UAPI control structs, and event dispatch in `virtio_card.c`.

## Risks and Test Signals
Risks include no explicit bounds checks against ALSA value array capacities for large `count`, type/access map indexing from device-provided values, TLV size trust and allocation pressure, event mask translation, and lifetime of devm item arrays. Test signals are boolean/int/int64/enum/bytes/IEC958 controls, TLV read/write/cmd, invalid metadata fuzzing, control notifications, and timeout/error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_kctl.c -->
