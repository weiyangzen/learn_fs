# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/procfs/procfs_test.go

## Purpose
Unit-tests the pure parsing portions of procfs discovery: client config key/value parsing, BeeGFS node connection parsing, and BeeGFS mount parsing.

## Important APIs, Types, And Functions
Tests `parseClientConfigFile`, `parseNodes`, and `parseMounts` using `strings.NewReader` inputs and `testify/assert`.

## Control Flow
`TestParseClientConfigFile` verifies simple config, whitespace-heavy config, and empty input. `TestParseNodes` verifies multiple node entries, root flag, TCP/RDMA/SDP peers, fallback route detection, no-connection nodes, and empty input. `TestParseMounts` verifies filtering BeeGFS mount lines from mixed `/proc/mounts` content, extracting `cfgFile`, mount path, options, and filesystem type.

## State And Persistence
No persistent state; tests construct in-memory readers and expected structs.

## Dependencies And Integration Points
Depends on `testing`, `testify/assert`, and common BeeGFS types. It indirectly documents expected procfs text formats consumed by `procfs.go`.

## Risks And Edge Cases
The tests cover happy-path parsing but not malformed input, scanner errors, missing node headers before connection lines, mounts without `cfgFile`, escaping in mount paths, or duplicate filesystem types beyond `ElementsMatch`.

## Test Signals
This file itself is the primary test signal for procfs parsing. It gives confidence for common formats but leaves operational discovery and error paths untested.
