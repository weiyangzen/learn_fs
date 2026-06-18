## sources/distributed-fs/ceph-client/include/linux/consolemap.h

Purpose: This header declares character translation helpers between VT console glyph maps, Unicode, and 8-bit encodings.

Important APIs, types, and functions: `enum translation_map` names `LAT1_MAP`, `GRAF_MAP`, `IBMPC_MAP`, and `USER_MAP`. Under `CONFIG_CONSOLE_TRANSLATIONS`, it exports `inverse_translate`, `set_translate`, `conv_uni_to_pc`, `conv_8bit_to_uni`, `conv_uni_to_8bit`, `console_map_init`, `ucs_is_double_width`, `ucs_is_zero_width`, `ucs_recompose`, and `ucs_get_fallback`. Disabled builds provide inline fallbacks that mostly return the glyph/input, reject code points above 0xff for PC glyph conversion, and report no width/recomposition/fallback metadata.

Control flow: The VT layer calls translation helpers while rendering or interpreting console bytes. The enabled path consults translation maps and Unicode tables; disabled paths bypass conversion.

State and persistence: Translation tables and user maps are implemented elsewhere. This header exposes no state directly, but `set_translate()` can return or install a per-VC translation table.

Dependencies and integration points: It depends on `struct vc_data`, `linux/types.h`, VT rendering, selection, and consolemap implementation.

Risks and test signals: Risks include incorrect glyph-to-Unicode mapping, missing double-width or zero-width handling, broken combining recomposition, and behavior divergence when translations are disabled. Test signals include Unicode console rendering, 8-bit charset tests, user map ioctls, width/fallback table tests, and builds with `CONFIG_CONSOLE_TRANSLATIONS=n`.
