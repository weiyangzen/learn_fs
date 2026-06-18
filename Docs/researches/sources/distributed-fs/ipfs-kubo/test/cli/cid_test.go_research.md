# sources/distributed-fs/ipfs-kubo/test/cli/cid_test.go

Purpose: black-box CLI coverage for `ipfs cid` subcommands: `inspect`, `base32`, `format`, `bases`, `codecs`, and `hashes`.

Important APIs/functions: `TestCidCommands`, `testCidInspect`, `testCidBase32`, `testCidFormat`, `testCidBases`, `testCidCodecs`, `testCidHashes`, and `assertExactSet`. It uses `go-cid`, libp2p `peer.ToCid`, and multihash construction for unknown-codec cases.

Control flow: subtests run CID commands without daemon setup, validate exact stdout/stderr, test JSON schema fields, convert CID versions/bases/codecs, feed stdin, and confirm mixed valid/invalid inputs return exit code 1 while still printing valid conversions.

State/persistence: no repo state or daemon persistence is required beyond harness temp command context; all inputs are literal CIDs or generated in memory.

Dependencies/integration: command parser/output layer, multibase registry, multicodec registry, multihash registry, libp2p-key CID handling, JSON encoder, and error aggregation for stream/list processing.

Risks/test signals: intentionally brittle registry lists catch accidental support changes. Emoji base output and exact spacing are output-format-sensitive; changes to supported codecs/hashes need coordinated test updates.
