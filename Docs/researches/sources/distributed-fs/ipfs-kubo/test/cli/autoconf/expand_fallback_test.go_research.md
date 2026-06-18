# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/expand_fallback_test.go

Purpose: verifies `--expand-auto` fallback behavior when AutoConf cannot fetch or parse remote data, when AutoConf is disabled, and when configs mix static and `auto` values.

Important functions: `TestExpandAutoFallbacks`, `testExpandAutoWithUnreachableServer`, `testExpandAutoWithDisabledAutoConf`, `testExpandAutoWithMalformedResponse`, `testExpandAutoMixedConfigPreservesStatic`, `testDaemonWithMalformedAutoConf`, and `loadTestDataForFallback`. The malformed-daemon test also uses `autoconf.GetMainnetFallbackConfig` to compare expected fallback bootstrap peers.

Control flow uses unreachable URLs, malformed JSON servers, valid fixture servers, and daemon-start flows. It runs `ipfs config Bootstrap --expand-auto`, `DNS.Resolvers --expand-auto`, and daemon health checks. Static peers surrounding `auto` must stay at the beginning/end after expansion. State is repo config, fallback output, and daemon cache/error handling. Dependencies include boxo AutoConf fallback constants, harness config setters, `httptest`, and JSON parsing. Risks include fallback fixture drift and the invalid port string `127.0.0.1:99999`, which depends on URL parsing/fetch error handling. Test signal ensures broken AutoConf services do not make daemons unusable and do not persist literal `auto` in expanded views.
