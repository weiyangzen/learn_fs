## sources/distributed-fs/ceph-client/drivers/staging/vc04_services/bcm2835-audio/vc_vchi_audioserv_defs.h

Purpose: this header defines the host-to-VideoCore audio service protocol messages used by the BCM2835 VCHIQ audio transport.

Important definitions: protocol versions are `VC_AUDIOSERV_MIN_VER` 1 and `VC_AUDIOSERV_VER` 2. Write completion cookies are fourcc values `BCMA` and `DATA`. `enum vc_audio_msg_type` defines result, complete, config, control, open, close, start, stop, write, and max message types. Payload structs cover config, control, open/close/start/stop, write, result, and completion. `struct vc_audio_msg` is the tagged union sent over VCHIQ.

Control flow and state: `bcm2835-vchiq.c` fills `vc_audio_msg` instances and sends them through VCHIQ. Synchronous commands wait for `VC_AUDIO_MSG_TYPE_RESULT`; audio payload writes expect later `VC_AUDIO_MSG_TYPE_COMPLETE` with matching cookies and a byte count.

Dependencies and integration points: depends on VCHIQ fourcc macros and Linux integer types via including code. It is private to the BCM2835 audio module and firmware ABI.

Risks: message structs cross a firmware boundary, so field sizes, signedness, endianness, and layout padding are ABI-sensitive. The enum comments are generic and several payload comments say "Configure audio" even for non-config operations, so the source is not self-documenting enough for protocol changes. Cookie validation protects completions only after the service accepts data.

Test signals: interoperability with firmware service version 1 and 2, config/control/open/start/stop/write round trips, completion cookie mismatch handling, and compile-time layout checks if available. Firmware protocol changes should be tested with both bulk and packetized write modes.
