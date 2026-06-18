# sources/distributed-fs/ipfs-kubo/test/cli/name_test.go

Purpose: broad integration suite for `ipfs name` publish, resolve, inspect, raw IPNS record get/put, sequence checks, offline behavior, TTL/lifetime validation, and republish config validation.

Important APIs/functions: `TestName`, `TestNameGetPut`, `TestNamePublishFlagValidation`, `TestNameRepublishConfigValidation`, and `TestNamePublishTTLClamp`. Inline helpers create daemons with imported fixture CAR data, generate keys, and create external IPNS records from ephemeral nodes.

Control flow: publish tests cover self keys across default/rsa/ed25519, named keys, CID/subpath/IPLD values, quiet output, offline resolution, V2-only records, TTL inspection, wrong-key validation, custom sequence numbers, and monotonic sequence enforcement. Get/put tests retrieve raw records, accept `/ipns/` prefixes, reject invalid/oversized/empty/garbage records, store external records, preserve bytes, handle offline `--allow-offline`, force lower-sequence puts, allow identical republish, and reject same-sequence different records.

State and persistence: imports fixture CAR blocks, publishes IPNS records to local/routing state, creates keys, writes record files, modifies repo config for republish validation, and starts/stops many daemons.

Dependencies/integration: depends on Boxo `ipns`, Kubo name command result structs, config validation, fixture CAR, harness DAG import, and routing record storage.

Risks: very stateful and daemon-heavy; public DHT avoidance relies on short lifetimes and test profiles. Sequence tests depend on IPNS “best record” semantics. Test signals are exact stdout/stderr, raw record bytes, JSON inspect validity, TTL/sequence values, and resolve output.
