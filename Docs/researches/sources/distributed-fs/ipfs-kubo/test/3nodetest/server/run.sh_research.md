# sources/distributed-fs/ipfs-kubo/test/3nodetest/server/run.sh

Purpose: runs the server side of 3nodetest by adding shared files to IPFS and publishing their CIDs through shared files.

Important APIs and control flow: adds bootstrap node from fig link env vars, starts `ipfs daemon --debug`, sleeps for startup, changes to `/tmp`, adds `/data/filetiny` and `/data/filerand`, writes CIDs via temp files renamed to `/data/idtiny` and `/data/idrand`, then sleeps for a long time so the client can retrieve data.

State and persistence: writes CID marker files to shared `/data`, creates daemon profiling output, and keeps the container alive.

Dependencies and integration: depends on bootstrap service, shared data container, IPFS CLI, and client polling.

Risks and test signals: fixed sleeps and very long final sleep make failures slow. No timeout or readiness check beyond sleep. Atomic-ish marker file rename prevents client seeing partial CID files.
