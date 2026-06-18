## sources/distributed-fs/ipfs-kubo/test/integration/addcat_test.go

Purpose: core integration test for UnixFS add/get across two in-memory Kubo nodes connected by libp2p mocknet under configurable latency.

Important APIs and control flow: tests call `DirectAddCat` with deterministic `RandomBytes`; epic variants use `SkipUnlessEpic` and larger/slow latency configs. `DirectAddCat` creates mocknet, builds online adder and catter `core.IpfsNode`s with mock hosts, links all peers, bootstraps each node to the other, adds bytes through `coreapi.NewCoreAPI(adder).Unixfs().Add`, retrieves via `catterAPI.Unixfs().Get`, copies the reader, and byte-compares output. `AddCatPowers` scales sizes by powers of two; `SkipUnlessEpic` skips unless `IPFS_EPIC_TEST` is set.

State and dependencies: state is in-memory node/blockstore/exchange state only; no repo persists. Dependencies include boxo bootstrap/files, Kubo core/coreapi/mock, libp2p mocknet, and latency configs.

Risks: large epic tests can be expensive; mocknet timing does not cover real network failures. Test signals are successful transfer and exact bytes under instantaneous, slow blockstore, slow network, slow routing, and large transfer scenarios.
