## sources/distributed-fs/ipfs-kubo/test/sharness/t0116-gateway-cache.sh

Purpose: tests gateway cache validators for generated UnixFS directory listings over both `/ipfs/` and `/ipns/` content paths.

Important APIs and helpers: uses fixture CAR import, offline IPNS record injection with `ipfs routing put --allow-offline`, `curl -svX GET`, and assertions on response header traces.

Control flow and state: imports a fixed fixture tree, maps an IPNS ID to the root, requests a nested directory listing through `/ipfs/<root>/root2/root3/` and `/ipns/<id>/root2/root3/`, then asserts both responses contain special `Etag` values beginning with `DirIndex` and including the resolved directory CID.

Dependencies and integration points: covers gateway UnixFS directory rendering, cache-control metadata, IPNS resolution to immutable CIDs, and generated HTML ETag construction.

Risks and test signals: catches cache validator regressions where generated listings share weak or incorrect ETags, especially when mutable IPNS paths resolve to immutable directory roots. Passing requires matching `DirIndex-..._CID-<ROOT3_CID>` headers.
