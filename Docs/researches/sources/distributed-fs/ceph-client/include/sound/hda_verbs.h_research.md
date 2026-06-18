# sources/distributed-fs/ceph-client/include/sound/hda_verbs.h

Source read summary: 568 lines, HD-audio verb, parameter, capability, pin, power, and stream-format constants.

Purpose: provides the protocol vocabulary for communicating with HDA codecs: node IDs, function groups, verbs, parameter IDs, widget capability fields, pin defaults, pin controls, amp fields, digital converters, power states, unsolicited responses, and PCM format/rate bits.

Important APIs, types, and functions: constants include `AC_VERB_*` get/set commands, `AC_PAR_*` parameters, `AC_WCAP_*` widget capabilities, connection-list and amp masks, `AC_PINCAP_*`, `AC_PINCTL_*`, EAPD bits, digital converter bits, power-state fields, GPIO verbs, stream/channel fields, default pin config extraction macros, and supported rate/format bit definitions. The header is almost entirely macros/enums and intentionally defines no runtime functions.

Control flow: HDA core and codec parsers compose verbs from this header, send them through bus command paths, parse responses using masks/shifts, choose PCM formats/rates, configure pins/amps/power, and decode unsolicited events.

State and persistence behavior: no software state is owned; the macros describe codec hardware register state and response encodings. Drivers cache selected values in codec structs or regmap for restore.

Dependencies and integration points: consumed by `hdaudio.h`, `hda_codec.h`, `hda_regmap.h`, HDMI codecs, and vendor codec parsers. It mirrors the Intel HD Audio specification and is ABI-adjacent for hwdep verb tools.

Risks and edge cases: bitfield drift breaks every codec parser; pin default decoding is especially sensitive to shift/mask accuracy; unsupported vendor quirks may overload standard fields.

Test signals: codec enumeration on varied vendors, parser pin/amp/power tests, raw verb hwdep validation, supported PCM query tests, HDMI pin/ELD flows, and compile checks for macro users.
