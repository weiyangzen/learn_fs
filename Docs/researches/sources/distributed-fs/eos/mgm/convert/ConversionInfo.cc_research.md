# sources/distributed-fs/eos/mgm/convert/ConversionInfo.cc

## Purpose
Implements the compact conversion descriptor used by the MGM converter. A conversion string encodes file id, target space/group, target layout id, optional placement policy, optional app tag, and optional ctime-update marker, and maps that descriptor to a proc conversion path.

## Important APIs and Functions
- `ConversionInfo::ConversionInfo` builds the canonical conversion string from typed fields.
- `ConversionInfo::parseConversionString` parses the string form back into a `ConversionInfo` object.
- `ConversionInfo::ConversionPath` shards conversion files under `gOFS->MgmProcConversionPath/<fid % 256>/<conversion-string>`.

## Control Flow
Parsing first strips trailing `+` for ctime update, validates a 16-hex-character fid before `:`, parses `<space.group>` before `#`, extracts optional `^app_tag^`, parses the layout hex up to optional `~`, parses optional placement policy, and rejects zero/invalid fid or layout. Successful parsing constructs a new canonical object, normalizing the string.

## State and Persistence
The object is immutable except for private `mConversionString`. The conversion path points into MGM proc namespace state; the file created at that path is later used by `ConversionJob` as the temporary converted file.

## Dependencies and Integration Points
Depends on `FileId`, `LayoutId`, `GroupLocator`, EOS logging, and global `gOFS` for proc path construction. It is consumed by `ConverterEngine`, `ConversionJob`, and `ConversionTag`.

## Risks
- The constant and path use `CONVERTION_SHARD_MOD`, preserving a misspelling but making naming brittle.
- The header comment mentions `[!]` while implementation uses `+` for ctime update.
- `std::stoull`/`std::stoll` parse failures are swallowed, and invalid values collapse to zero; zero is rejected, so fid 0/layout 0 cannot be represented.
- Optional app tags are delimited by `^`; tags containing `^` cannot round-trip safely.

## Test Signals
Tests should cover valid round trips with/without group, policy, app tag, and ctime; malformed fid/layout/space/app delimiters; shard path formatting; and normalization of parsed strings.
