# sources/distributed-fs/ceph-client/sound/firewire/tascam/amdtp-tascam.c

## Purpose

This file implements TASCAM's custom AMDTP payload handling. It converts between ALSA S32 PCM buffers and TASCAM data blocks, applies PCM constraints, and extracts status/control messages from incoming isochronous packets.

## Important APIs, types, and functions

`amdtp_tscm_init()` initializes an AMDTP stream with TASCAM format IDs and callbacks. `amdtp_tscm_set_parameters()` sets data channels, adding two extra channels for input streams. PCM helpers read/write S32 samples; `read_status_messages()` updates `tscm->state` and enqueues hwdep change events. `amdtp_tscm_add_pcm_hw_constraints()` declares 24 significant bits in 32-bit samples.

## Control flow

Incoming payload processing optionally copies PCM frames, then scans every data block's counter/state trailer. For selected state indexes, masked changes are queued to `tscm->queue` and `hwdep_wait` is woken. Outgoing payload processing writes PCM frames or silence. Initialization chooses `process_ir_ctx_payloads` for device-to-host streams and `process_it_ctx_payloads` for host-to-device streams, with nonblocking, skip-DBC-zero, and SYT-unaware flags.

## State and persistence behavior

Protocol state stores fixed PCM channel count. Driver state updated here includes `tscm->state`, circular control-change queue positions, and PCM buffer pointers managed by AMDTP core.

## Dependencies and integration points

It depends on `amdtp-stream`, TASCAM stream setup, ALSA PCM runtime buffers, and hwdep readers that drain queued control changes.

## Risks and test signals

Risks include queue overwrite, endianness mistakes, state mask omissions, buffer wrap errors, and wrong channel counts after model spec changes. Tests should cover PCM capture/playback, silence output, status-event generation, queue wrap, high-rate streams, and hwdep state ioctl consistency.
