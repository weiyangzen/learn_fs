# sources/distributed-fs/ipfs-kubo/core/coreapi/block.go

Purpose: implements CoreAPI block operations for raw block put/get/remove/stat.

Important APIs/types/functions: `BlockAPI`, `BlockStat`, and methods `Put`, `Get`, `Rm`, `Stat`, plus `BlockStat.Size`/`Path`.

Control flow: `Put` parses options, reads all source bytes, builds a CID with the selected prefix, constructs a block, optionally acquires pin lock, adds the block, optionally recursively pins and flushes. `Get` and `Stat` resolve the input path then fetch the root block. `Rm` resolves the path, calls `blockstoreutil.RmBlocks` with force settings, and consumes one result or context cancellation.

State and persistence behavior: `Put` writes blocks to blockservice/blockstore and may update pin state. Pinning flushes pinner state. `Rm` removes blockstore data subject to pin constraints. Reads are non-mutating.

Dependencies and integration points: uses Kubo tracing, `coreiface/options`, blockstore util removal, boxo path/pinning/block APIs, and CoreAPI path resolution.

Risks: `Put` reads the entire block into memory, appropriate for block API but risky for unbounded callers. Pin lock is only taken when pinning. `Rm` consumes only the first removal result, which matches single-CID removal but would need care if expanded.

Test signals: covered through CoreAPI interface tests in `coreapi/test/api_test.go`; repo verify tests use a mocked `BlockAPI.Get`.
