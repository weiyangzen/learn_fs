# Research: sources/cloud-native/moby/daemon/libnetwork/internal/addrset/addrset_test.go

Purpose: thoroughly exercises `AddrSet` allocation, removal, counting, range counting, and error mapping. Important tests include `TestIPv4Pool`, `TestIPv6Pool`, `Test64BitIPv6Range`, `Test32BitIPv6Range`, `TestFullPool`, `TestNotInPool`, `TestInvalidPool`, and `Test64BitPlusAllocation`.

Control flow: tests add first/last addresses, duplicate addresses, remove absent and present entries, allocate serial addresses, allocate within subranges, and count addresses in overlapping/non-overlapping prefixes. Large IPv6 tests ensure pools wider than one bitmap split correctly and 2^64 counts are represented with high/low uint64 values. A helper `uint128Equal` compares split counts using `big.Int`.

State/dependencies: tests inspect internal bitmap maps directly, including synthetic binary bitmap setup to avoid expensive allocation loops. Dependencies include `netip`, encoding/binary, big integers, and `gotest.tools`. Risks covered include host bits in prefixes, bitmap cleanup, duplicate errors, invalid prefixes, full-pool exhaustion, and overflow. Gaps include concurrent access and randomized non-serial allocation behavior.
