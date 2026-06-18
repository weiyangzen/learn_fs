# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/httpfetcher.go

Purpose: implements HTTP gateway-based migration fetching using verifiable trustless CAR retrieval.

Important APIs and control flow: `NewHttpFetcher` normalizes distribution path, gateway, user agent, and fetch limit. `Fetch` resolves the dist path to an immutable path, requests a CAR from the gateway, and extracts the requested UnixFS file through `carStreamToFileBytes`. Mutable IPNS paths are resolved by fetching and validating IPNS records; DNSLink uses the default multiaddr DNS resolver. HTTP requests set both Accept and `?format=` hints and enforce body limits when configured.

State and persistence: no disk persistence; builds temporary in-memory datastore/blockstore/DAG service for CAR verification and extraction.

Dependencies and integration: uses Boxo blockservice, path resolver, IPNS/namesys, CAR v2, go-unixfsnode, and an HTTP client with migration-specific timeouts. Used by legacy migration download fetchers.

Risks and test signals: third-party gateway content is verified by CID path, but IPNS/DNSLink resolution depends on gateway/DNS availability. Large CARs are limited by reader but file bytes are read fully into memory. Tests cover user agent, fetch success, 404, invalid CAR failover, and gateway rotation.
