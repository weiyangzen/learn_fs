<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/network_address_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/network_address_unittest.cc

## Purpose
Tests `NetworkAddress::toString` formatting. The source was read completely for this report.

## Important APIs, Types, And Functions
Constructs addresses with IP `0x0A00FF10`, port 9425/0, and zero IP/port.

## Control Flow
Straight-line expectations verify dotted-quad rendering and optional port suffix.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Depends on gtest and `network_address.h`.

## Risks And Edge Cases
Does not test serialization, hashing, comparisons, or exception text.

## Test Signals
Passing tests protect the display form used in errors/logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/network_address_unittest.cc -->
