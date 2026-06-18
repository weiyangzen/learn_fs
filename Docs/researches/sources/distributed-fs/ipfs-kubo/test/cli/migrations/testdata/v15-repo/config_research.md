# sources/distributed-fs/ipfs-kubo/test/cli/migrations/testdata/v15-repo/config

Purpose: static Kubo repo config fixture representing repository version 15 for migration tests.

Important structure: JSON config includes `Identity` with fixed peer/private key, legacy datastore mount spec using measure wrappers, concrete swarm/API/gateway addresses, default bootstrap peers, `Routing` with null `Routers`/`Methods`, `Ipns`, `DNS.Resolvers`, `Migration`, legacy `Provider` with `Strategy`, `Reprovider`, `Experimental`, `Plugins`, `Pinning`, `Import`, and `Internal`.

Control flow/integration: it is not executable code; tests copy this directory into temp repos via `cloneStaticRepoFixture` and use it as the pre-migration state for hybrid v15-to-latest and latest-to-v15 downgrade scenarios.

State and persistence: persistent fixture data includes sensitive-looking but test-only identity material. Tests must copy it before mutation so the fixture remains stable.

Dependencies/integration: consumed by `setupStaticV15Repo`, mock external migration tests, and JSON assertions around preserved peer ID, bootstrap presence, and `AutoConf` changes.

Risks: because it contains fixed listen ports (`4001`, `5001`, `8080`), daemon tests may need migration/runtime code to adjust or tolerate port use. Drift between this fixture and real historical v15 repos can reduce coverage value. Test signals are valid JSON, version-paired config shape, and legacy fields that embedded/external migrations transform.
