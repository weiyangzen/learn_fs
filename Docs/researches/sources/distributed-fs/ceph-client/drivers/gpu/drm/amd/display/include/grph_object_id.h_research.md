# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/grph_object_id.h

Purpose: Defines the compact graphics object identifier model used across AMD Display Core. It enumerates object types, object enum IDs, generic/controller/clock/encoder/connector/audio/engine IDs, color depth, DP alt mode, and a 32-bit `struct graphics_object_id` bitfield wrapper.

Important APIs and types: `enum object_type`, `enum object_enum_id`, `enum generic_id`, `enum controller_id`, `enum clock_source_id`, `enum encoder_id`, `enum connector_id`, `enum audio_id`, `enum engine_id`, `enum transmitter_color_depth`, `enum dp_alt_mode`, and `struct graphics_object_id`. Inline helpers initialize, pack to uint, compare, extract typed IDs, and test analog connector support.

Control flow: Callers construct object IDs with `dal_graphics_object_id_init`, pass them through topology/resource APIs, and use typed getters to safely recover IDs only when `type` matches. `dal_graphics_object_id_to_uint` packs `id`, `enum_id`, and `type` according to the bitfield layout.

State and persistence: No dynamic state. The packed bit layout is explicitly intended to stay simple and stable: 8 bits ID, 4 bits enum, 4 bits type, 16 reserved bits. This value is persisted in tables and comparisons throughout DC.

Dependencies and integration points: Has no includes by design. Used by BIOS parser data, connector layout, integrated info, resource construction, and display topology. Analog support helper influences connector/signal decisions for VGA and DVI-I.

Risks: The header relies on C bitfield layout assumptions for the struct while `to_uint` manually recreates expected layout; cross-compiler or endian subtleties should be considered. Enum aliases such as `ENGINE_ID_UNKNOWN = -1L` in an enum with positive values must be handled carefully. Adding IDs beyond bit widths would truncate in packed form.

Test signals: Static assertions for `sizeof(struct graphics_object_id) == 4`, round-trip tests for init/to_uint/type getters, equality checks, and connector analog support matrix coverage.
