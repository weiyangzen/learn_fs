# sources/distributed-fs/ceph/src/rgw/rgw_formats.cc

## Purpose
Implements RGW-specific formatters: a legacy/plain formatter for simple responses and an HTML formatter for Swift static website directory listings.

## Important APIs, Types, And Functions
`RGWFormatter_Plain` implements `Formatter` methods for opening/closing sections, dumping scalar values, buffering output, flushing, and reset. `write_data()` handles dynamic buffer growth around `vsnprintf()`. `HTMLHelper` exposes XML escaping. `RGWSwiftWebsiteListingFormatter` generates header/footer rows and object/subdir rows.

## Control Flow
Plain formatter tracks a section stack and prints only the first value at the minimum stack level unless `use_kv` is enabled. Dumps append to an internal null-terminated buffer and `flush()` writes it to an output stream. Swift listing formatter writes a complete HTML table with optional stylesheet link, parent row, escaped/link-encoded object names, sizes, and mtimes.

## State And Persistence Behavior
All state is in-process formatting state: buffer pointer/length/capacity, stack, `min_stack_level`, `use_kv`, and `wrote_something`. No persistence.

## Dependencies And Integration Points
Uses Ceph `Formatter`, `XMLFormatter`, RGW common/rest helpers, URL encoding, XML escaping, `dump_time_to_str()`, and Boost format. Used by RGW response paths that need plain, key/value, or Swift website listing output.

## Risks
`dump_stream()` aborts. Manual malloc/realloc/free and null-termination require care. `close_section()` assumes a non-empty stack. Plain formatting is documented as a hack and may not match structured formatter semantics. HTML output must continue escaping names to avoid injection.

## Test Signals
Tests should cover scalar dumps in plain and key/value modes, nested sections, buffer growth beyond 4096 bytes, flush/reset reuse, object/subdir HTML escaping, CSS path URL encoding, and parent row generation.
