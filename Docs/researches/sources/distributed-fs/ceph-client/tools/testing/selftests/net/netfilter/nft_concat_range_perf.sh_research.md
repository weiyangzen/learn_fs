## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_concat_range_perf.sh

Purpose: extended/performance-only wrapper for `nft_concat_range.sh`.

Important APIs and tools: sources `lib.sh`, checks `KSFT_MACHINE_SLOW`, sets environment variable `NFT_CONCAT_RANGE_TESTS=performance`, and `exec`s `./nft_concat_range.sh`.

Control flow: if running on a slow-machine kselftest environment, exits skip immediately. Otherwise it replaces itself with the main concat-range suite limited to the `performance` group.

State and persistence: no independent state; all setup/cleanup is delegated to `nft_concat_range.sh`. Dependencies are the main script, performance tools/pktgen availability, and root. Risks are that performance tests are environment-sensitive and may skip internally if pktgen is unavailable. Test signal is inherited exit/output from the main script.
