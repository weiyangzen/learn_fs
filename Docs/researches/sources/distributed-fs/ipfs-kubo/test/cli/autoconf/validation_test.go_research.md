# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/validation_test.go

Purpose: daemon-level validation tests ensuring invalid AutoConf payloads do not prevent daemon startup and do not become trusted cached configuration.

Important functions: `TestAutoConfValidation`, `testInvalidAutoConfJSONPreventsCaching`, `testMalformedMultiaddrInAutoConf`, and `testMalformedURLInAutoConf`. Each creates an `httptest` AutoConf server returning invalid payloads: malformed bootstrap multiaddrs, invalid mixed multiaddr lists, or malformed DNS resolver URLs.

Control flow configures a test-profile node with `AutoConf.URL`, `AutoConf.Enabled=true`, and relevant `auto` config fields, starts the daemon, then runs `ipfs version` to prove daemon health. The first test also counts server requests to confirm validation was attempted. State includes daemon process, attempted remote payload, and any cache behavior inside the repo. Dependencies are AutoConf validation code, harness daemon startup, and JSON/URL/multiaddr parsing. Risks include tests not directly inspecting cache absence, only daemon survival and fetch attempt. Test signal protects graceful degradation: invalid remote AutoConf must be rejected without making core CLI commands unavailable.
