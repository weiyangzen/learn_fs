# sources/distributed-fs/ceph-client/sound/soc/codecs/cirrus_legacy.h

## Purpose
`cirrus_legacy.h` provides a small helper for older Cirrus Logic codec drivers that expose a 20-bit device ID across three adjacent registers.

## Important APIs And Functions
`cirrus_read_device_id(struct regmap *regmap, unsigned int reg)` bulk-reads three bytes from `reg`, returns a negative regmap error on failure, and otherwise composes the ID as bits `[19:12]` from byte 0, `[11:4]` from byte 1, and `[3:0]` from the high nibble of byte 2.

## Control Flow And State
The helper is stateless and inline. Callers use it during probe or identification paths to normalize legacy device ID reads.

## Dependencies And Integration Points
It depends on regmap and `ARRAY_SIZE()` being available in the including translation unit. It is intended for local inclusion by Cirrus codec drivers rather than as a standalone module.

## Risks And Test Signals
Because it is a header-only helper without include guards or includes, consumers must include appropriate Linux headers first and avoid multiple conflicting definitions in unusual contexts. Test signals include regmap bulk-read success, correct ID composition for known devices, and propagation of read errors.
