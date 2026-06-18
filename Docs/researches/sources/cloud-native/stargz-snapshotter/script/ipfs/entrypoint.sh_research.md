# sources/cloud-native/stargz-snapshotter/script/ipfs/entrypoint.sh

Purpose: Starts an offline IPFS daemon before running a supplied command.
Important APIs/types/functions: IPFS init/daemon startup and curl readiness probe; final `$@` execution.
Control flow: initializes IPFS, runs daemon offline in background, waits for API `/version`, then executes the container command.
State and persistence: creates IPFS repository under default IPFS path inside the container.
Dependencies and integration points: used by `ipfs/test.sh` to run Go IPFS client tests.
Risks: does not clean up daemon explicitly; `$@` is unquoted in source and can split unusual arguments.
Test signals: readiness is validated by curl before tests start.
