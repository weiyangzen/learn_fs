# sources/distributed-fs/openafs/src/butc/config

## Purpose
`config` is a one-line local configuration/data file for the `butc` source directory. Its content is `200000 /tmp`, which appears to describe a numeric capacity or threshold paired with a temporary directory path.

## Important APIs, Types, And Functions
There are no functions or types. The important data fields are the integer-like value `200000` and the path `/tmp`.

## Control Flow
There is no control flow in the file. Any behavior depends on consumers elsewhere in the coordinator or test tooling parsing the line.

## State And Persistence
The file is static repository data. It may influence runtime or test behavior if copied/read as a coordinator configuration input, but this file itself performs no persistence.

## Dependencies And Integration Points
No direct dependency is visible inside the file. Integration must be discovered from consumers that open `src/butc/config` or install it alongside Tape Coordinator tooling.

## Risks And Test Signals
Risks are format ambiguity and hard-coded `/tmp` assumptions. Test signals should search for consumers, verify the expected numeric unit, and confirm behavior when `/tmp` lacks space, is mounted with restrictive options, or the line is malformed.
