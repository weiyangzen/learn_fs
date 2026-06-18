<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CommandHandler.h -->
# sources/distributed-fs/ceph/src/mon/CommandHandler.h

## Purpose
`CommandHandler.h` declares a common base helper for monitor command handlers. It currently standardizes parsing of true/false-like command arguments.

## Important APIs, types, and functions
`class CommandHandler` exposes `int parse_bool(std::string_view str, bool* result, std::ostream& ss)`. The documented contract requires a non-null `result`, returns zero on success, returns `-EINVAL` on parse failure, and uses the stream for an explanatory error message.

## Control flow
The header contains no executable flow beyond the interface contract. Implementations include this header and call `parse_bool()` when converting command-map values into booleans.

## State and persistence behavior
The class has no fields and no persistence. It is a stateless utility object/base class.

## Dependencies and integration points
The header depends only on forward declarations via `<iosfwd>` and `std::string_view`. It can be included widely without pulling in monitor internals.

## Risks and edge cases
Because the helper is not static, users need an instance or base class relationship to call it. Adding more parsing helpers here would affect all monitor code that includes this common header, so dependencies should remain light.

## Test signals
Compile tests should verify inclusion from command handler implementations without extra dependencies. Functional signals come from `CommandHandler.cc` boolean parsing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CommandHandler.h -->
