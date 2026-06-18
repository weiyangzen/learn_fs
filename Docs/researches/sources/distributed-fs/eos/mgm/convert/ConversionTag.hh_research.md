# sources/distributed-fs/eos/mgm/convert/ConversionTag.hh

## Purpose
Provides a small static helper for producing conversion tag strings from fid, space, layout id/string, placement policy, and ctime-update choice.

## Important APIs and Types
- `ConversionTag::Get(fid, space, unsigned int layoutid, plctplcy, ctime_update)` formats the layout id as eight hex digits and delegates.
- `ConversionTag::Get(fid, space, std::string conversion, plctplcy, ctime_update)` builds `<fid16hex>:<space>#<layout><~policy><+>`.

## Control Flow and State
The helper is stateless. It prepends `~` to non-empty placement policy and appends `ConversionInfo::UPDATE_CTIME` when requested.

## Dependencies and Integration Points
Includes `XrdMgmOfs` and `ConversionInfo`, though it only needs the update marker from `ConversionInfo`. Its output is intended to be parsed by `ConversionInfo::parseConversionString`.

## Risks
- This helper does not include the scheduling group index style emitted by `ConversionInfo` constructor (`space.index`), only the caller-provided `space` string.
- No app tag support, so newer conversion strings with `^app_tag^` cannot be produced through this class.
- Fixed buffers rely on `snprintf`; overly long inputs are truncated silently.
- Header includes `XrdMgmOfs` unnecessarily, increasing compile coupling.

## Test Signals
Tests should verify layout formatting, policy separator insertion, ctime marker behavior, parser round-trip with `ConversionInfo`, and long-input truncation behavior if considered acceptable.
