# sources/distributed-fs/ipfs-kubo/test/3nodetest/bin/save_profiling_data.sh

Purpose: copies profiling artifacts from 3nodetest containers into the build directory.

Important APIs and control flow: loops over bootstrap/client/server to copy `/go/bin/ipfs` and `/go/ipfs.cpuprof`, then copies `/go/ipfs.memprof` from bootstrap and server. Client memprof is skipped because the client daemon is not terminated.

State and persistence: writes profiling files under `build/profiling_data_<container>`.

Dependencies and integration: depends on Docker and containers running with `IPFS_PROF`/debug profiling output.

Risks and test signals: hard-coded container names and paths. `docker cp` failures stop the script unless caller ignores errors; the main runner does ignore failures. No tests.
