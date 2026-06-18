# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-helpers.h

## Purpose
Declares EC utility APIs and inline stripe-alignment helpers shared by the EC translator implementation.

## Important APIs, types, and functions
Macros `EC_ERR()`, `EC_IS_ERR()`, and `EC_GET_ERR()` encode small negative errors as pointers. `EC_ALIGN_CHECK()` checks required memory alignment. Function declarations cover tracing, iov copying, aligned buffer allocation, dict xattr encode/decode, loc normalization, owner assignment, inode/fd context lookup, inode read-mask access, internal xattr filtering, replace-heal launch, and read-mask parsing. Inline geometry helpers are `ec_adjust_size_down()`, `ec_adjust_size_up()`, `ec_adjust_offset_down()`, and `ec_adjust_offset_up()`. `ec_is_power_of_2()` supports option/config validation.

## Control flow
The inline adjustment helpers convert user-visible logical sizes/offsets into EC stripe or fragment boundaries. Down-adjust returns the head remainder and optionally divides by `ec->fragments`. Up-adjust rounds to the next stripe/fragment boundary, returning the tail bytes needed; the size variant marks unsigned overflow by setting `UINT64_MAX` and returning a negative tail, while the offset variant clamps to `GF_OFF_MAX` on signed overflow.

## State and persistence behavior
The header itself stores no state, but its dict APIs define the persistent representation of EC xattrs and its adjustment helpers control how logical file sizes, brick fragment offsets, and heal/truncate/read sizes are interpreted throughout the translator.

## Dependencies and integration points
Included by EC heal, read, write, common, and translator setup code. It depends on `ec-types.h` for `ec_t`, `ec_config_t`, fd/inode contexts, and fop types. Its prototypes bridge source files that otherwise share no implementation unit, especially `ec-heal.c`, `ec-inode-read.c`, and `ec.c`.

## Risks and test signals
The alignment helpers are high impact: an off-by-one or overflow bug can corrupt read ranges, write ranges, heal windows, and size xattrs. Tests should cover aligned and unaligned sizes/offsets, scaled and unscaled conversions, near-`UINT64_MAX` and near-`GF_OFF_MAX` values, zero stripe edge assumptions, pointer-error macro round trips, and header/implementation signature consistency.
