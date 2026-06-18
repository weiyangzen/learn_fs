# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/delta/delta-mjpeg-fw.h

Purpose: defines the MJPEG firmware ABI structures, enumerations, and status codes exchanged through Delta IPC.

Important APIs and types: includes decoded/display buffer address structures, reconstruction-output enable flags, horizontal/vertical decimation factors, `enum jpeg_decoding_error_t`, decode mode and additional flags, `struct jpeg_video_decode_init_params_t`, `struct jpeg_decode_params_t`, and `struct jpeg_decode_return_params_t`.

Control flow: no executable code. `delta-mjpeg-dec.c` fills init/decode parameter structures in the IPC shared buffer and firmware writes the return-params structure after decode.

State and persistence: no driver state. These layouts are part of the host/firmware binary contract and must remain fixed-width and alignment-compatible.

Dependencies and integration points: depends on kernel integer types. The fields are consumed by the MJPEG decoder and transported by `delta-ipc.c`.

Risks: enum and structure sizes must match firmware expectations across compiler/architecture combinations. All physical-address fields are `u32`, which assumes firmware-visible addresses fit 32 bits. A typo-like vertical decimation value `0x000000208` should be treated cautiously even if unused. Extending structures without firmware coordination will break IPC.

Test signals: firmware interoperability, decode command dumps, status error-code mapping, and builds on 32/64-bit configurations to confirm structure sizes remain expected.
