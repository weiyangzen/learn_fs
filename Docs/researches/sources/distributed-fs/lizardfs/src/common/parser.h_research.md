<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/parser.h -->
# sources/distributed-fs/lizardfs/src/common/parser.h

## Purpose
Declares the parser base class and protected numeric conversion helpers. The source was read completely for this report.

## Important APIs, Types, And Functions
`Parser::Status`, `consume` overloads, protected `data/position/previousPosition`, `getHexValue`, `getDecValue`, and private `intFromHexString/intFromDecString` define the API for derived parsers.

## Control Flow
Template conversion helpers parse the last consumed substring as signed/unsigned hex or decimal using `stoll/stoull`.

## State And Persistence Behavior
Parser state is per object: copied input string and cursor positions.

## Dependencies And Integration Points
Depends on `platform.h` for compatibility `std::stoull` and standard exceptions.

## Risks And Edge Cases
Hex length check uses `length/2 > sizeof(T)` and may not reject all odd-length overflows; signedness casts can wrap.

## Test Signals
Derived parser tests should include malformed numbers, negative values into unsigned types, and substring positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/parser.h -->
