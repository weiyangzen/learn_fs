# sources/distributed-fs/ipfs-kubo/test/3nodetest/client/run.sh

Purpose: runs the client side of the three-node integration test, fetching files from IPFS and comparing them to shared-volume originals.

Important APIs and control flow: adds the bootstrap node from fig link env vars, starts `ipfs daemon --debug` in background, waits for `/data/idtiny`, cats the tiny CID to a file, diffs it against `/data/filetiny`, waits for `/data/idrand`, cats the random CID, checks command status, diffs against `/data/filerand`, and prints success.

State and persistence: writes fetched files in `/tmp`; reads CID marker files and original data from `/data`; starts a long-running daemon that produces profiling files.

Dependencies and integration: depends on server writing CID files, bootstrap service, shared data volume, and shell arithmetic syntax under bash.

Risks and test signals: no timeout while waiting for marker files, so failures can hang. Background daemon is not explicitly stopped, which affects memprof collection. Full test success is the primary signal.
