# sources/distributed-fs/ipfs-kubo/test/cli/cid_base_test.go

Purpose: integration coverage for global `--cid-base` formatting across CLI commands that create, inspect, remove, or display CIDs. The test uses an offline daemon and `base16`, expecting CIDv1 strings beginning with `f01` so default base32 changes cannot create false positives.

Important APIs/functions: `TestCidBase`, local `makeDaemon`, `harness.Node` helpers `Init`, `StartDaemon`, `IPFSAddStr`, `PipeStrToIPFS`, `PipeToIPFS`, and `IPFS`; JSON decoding of `dag stat` output.

Control flow: subtests add blocks/files, run commands with and without `--cid-base=base16`, and assert CIDv0 values are upgraded for display when a non-base58btc base is requested. Coverage includes `add`, `pin ls`, `dag import`, `block put/stat/rm`, `dag stat`, `object patch`, `refs local`, and `object diff`.

State/persistence: each subtest owns a temporary initialized repo and daemon, writes MFS directories for object patch/diff, imports CAR bytes through stdin, and removes blocks for `block rm`.

Dependencies/integration: exercises the CLI formatting layer, blockservice, DAG import/export, MFS/object commands, refs, pinning, and the harness daemon runner.

Risks/test signals: strong regression signal for output encoding consistency. Risk is broad command coverage under parallel subtests can expose daemon startup/resource contention; assertions depend on human-readable outputs containing CIDs.
