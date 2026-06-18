## sources/distributed-fs/ipfs-kubo/test/sharness/t0600-issues-and-regressions-online.sh

Purpose: online regression collection for HTTP API behavior, metrics, pin API response shape, malformed upload handling, offline daemon/mount behavior, and IPNS operations in offline-network daemon mode.

Important commands and control flow: starts a daemon with a non-empty repo, checks `/api/v0/commands?flags`, confirms `/api/v0/refs/local` returns NDJSON-like fields, posts to an arg-stdin command without crashing, checks daemon stderr for no panic, fetches Prometheus metrics, validates `pin/add` and `pin/rm` JSON responses, optionally uses `socat` to send malformed multipart data and expect 500 without daemon crash, then checks `ipfs daemon --offline --mount` fails. It restarts without network and publishes/resolves the self key offline.

State and persistence: involves daemon state, metrics endpoint, pins, key/IPNS records, and daemon stderr. It stops and restarts daemons across online and offline-network modes.

Dependencies and integration points: depends on HTTP API routes, metrics registry, pinning, multipart parser, `socat` prereq, IPNS publish/resolve, key listing, and sharness daemon helpers.

Risks and test signals: broad smoke coverage but sensitive to exact JSON ordering and metrics names. The offline IPNS section catches local routing/resolution regressions after daemon identity operations.
