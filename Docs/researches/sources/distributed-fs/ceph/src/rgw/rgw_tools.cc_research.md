# sources/distributed-fs/ceph/src/rgw/rgw_tools.cc

## Purpose
`rgw_tools.cc` initializes and queries a MIME type map used by RGW based on extension-to-MIME mappings from a configured file.

## Important APIs, Types, and Functions
`parse_mime_map_line()` skips leading whitespace, splits a line on whitespace, treats the first token as MIME type, and maps each remaining extension to it. `parse_mime_map()` iterates lines. `ext_mime_map_init()` reads the configured file safely and fills the map. `rgw_find_mime_by_ext()` looks up an extension. `rgw_tools_init()` allocates and populates the global map. `rgw_tools_cleanup()` releases it.

## Control Flow
Initialization allocates a transparent-comparator map, attempts to read `rgw_mime_types_file`, ignores initialization errors, and leaves lookups available. File-size races cause a recursive retry.

## State and Persistence Behavior
The only state is the process-global `ext_mime_map`; no persistent writes occur.

## Dependencies and Integration Points
Depends on Ceph safe I/O, config, split utility, error logging, and `driver/rados/rgw_tools.h`. RGW object serving code uses the MIME lookup when deriving content types.

## Risks
`rgw_find_mime_by_ext()` assumes `rgw_tools_init()` has run. Recursive retry on file-size race could loop if the file changes constantly. Parse logic does not skip comment lines explicitly unless split behavior or file format makes them harmless.

## Test Signals
Cover missing mime file, comments/blank lines, multiple extensions per MIME type, lookup before/after cleanup, file-size race handling, and transparent `string_view` lookup.
