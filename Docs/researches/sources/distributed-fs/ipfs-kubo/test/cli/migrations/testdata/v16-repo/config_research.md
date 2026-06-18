# sources/distributed-fs/ipfs-kubo/test/cli/migrations/testdata/v16-repo/config

Purpose: static Kubo repo config fixture representing repository version 16, used as the main migration baseline.

Important structure: JSON config includes fixed `Identity`, datastore mount spec with flatfs and levelds, random-port addresses for swarm/API/gateway, `Mounts.MFS`, default bootstrap peers including DNS addr entries, gateway/API headers, swarm transport/resource sections, `AutoTLS`, empty `Routing`, `Provider`, `Reprovider`, `HTTPRetrieval`, import tuning null fields, `Version`, `Internal`, and `Bitswap`.

Control flow/integration: copied by `setupStaticV16Repo` for v16-to-latest, v17 setup, and concurrent migration tests. Migration assertions inspect how this config gains `AutoConf`, replaces default bootstrap/delegated routing/IPNS/DNS values with `auto`, and later moves Provider/Reprovider into Provide.

State and persistence: persistent fixture data is immutable source input for tests; temp copies are mutated by repo/daemon migration commands and backup creation.

Dependencies/integration: paired with a repo `version` file and other fixture files in `testdata/v16-repo`. Used by JSON helpers that compare map/list values.

Risks: fixture has current migration assumptions baked in, especially repo version sequence and default bootstrap values. If historical defaults or latest repo version change, tests may require fixture or assertion updates. Test signals are valid JSON and expected legacy-to-latest field transformations.
