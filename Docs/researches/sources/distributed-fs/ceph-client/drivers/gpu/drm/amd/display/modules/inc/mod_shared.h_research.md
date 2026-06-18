# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_shared.h

Purpose: provides small shared enums and structs used by multiple display modules, especially color transfer functions, VRR packet types, and 3D LUT control metadata.

Important APIs/types: `enum color_transfer_func` covers SRGB, BT709, PQ, linear, and gamma encodings. `enum vrr_packet_type` identifies VRR, FreeSync versions, and VTEM packet generation. `union lut3d_control_flags` exposes a raw 32-bit value plus bitfields for gamut, chroma, black handling, shaper, gamma, and 3D LUT usage. `struct lut3d_settings` combines flags, luminance limits, gamut-map mode, and rotation mode.

Control flow role: header-only data contract; implementation files inspect these values when building packets or programming display color behavior.

State and persistence: callers persist `lut3d_settings` and pass transfer/packet enums through module APIs. The bitfield union is a serialization-sensitive state container.

Dependencies and integration: included by FreeSync and info-packet interfaces. It avoids heavyweight DC includes, making it a common module-level contract.

Risks: bitfield ordering can be compiler/ABI sensitive if serialized externally. The `reseved` typo is part of the field name and should not be casually changed if code references it. Enum expansion must be coordinated with packet builders.

Test signals: compile coverage for all includes, raw bitfield round-trip tests where serialized, transfer-function selection in VSC packet generation, and LUT settings compatibility across modules.
