# Research: sources/cloud-native/buildkit/cmd/buildctl/cachemetrics.go

Purpose: implements the optional `--debug-json-cache-metrics` build output that summarizes cache behavior from streamed `client.SolveStatus` vertex updates. It helps users inspect cache misses without parsing full progress JSON.

Important APIs and flow: `vtxInfo` tracks vertex cached/completed/from/name booleans. `tailVTXInfo` consumes the status channel until close, records every vertex by digest, marks Dockerfile `FROM` vertices using a regexp, and records cached/completed state. `outputCacheMetrics` computes total, completed, user total, user cached/completed/cacheable, `FROM`, miss count, and client duration, writes one line per non-FROM user cache miss, then writes a JSON metrics object.

State and dependencies: all state is in-memory and derived from progress stream tails. It depends on `client.SolveStatus`, OCI digests, regexp matching, and elapsed wall-clock time from build start.

Risks and test signals: metrics are heuristic because vertex names classify internal/auth/import/export and `FROM` operations by strings. Name changes in progress output can skew counts. There is no direct unit test in this group; coverage is indirect through build progress code paths.
