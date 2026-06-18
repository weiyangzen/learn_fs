# sources/cloud-native/containerd/core/content/content.go

Purpose: central content store interface definitions and option types.

Important APIs/types: `Store` combines `Manager`, `Provider`, `IngestManager`, and `Ingester`. `ReaderAt` adds `Size` and `Close`. `Provider.ReaderAt`, `Ingester.Writer`, ingest management methods, `Info`, `Status`, `WalkFunc`, `InfoProvider`, `Manager`, and `Writer` define the content lifecycle. `Syncer`, `ReferrersProvider`, `Opt`, `WithLabels`, `WriterOpts`, `WriterOpt`, `WithDescriptor`, and `WithRef` complete the contract.

Control flow and state: no implementation. Comments define lifecycle semantics: writes are invisible until commit, active ingestions are tracked by ref, committed content is queried by digest, and commit closes the writer.

Dependencies and integration: OCI descriptors and opencontainers digests are the exchange currency. Implementations include local stores, metadata stores, and remote proxies.

Risks: behavior such as resumability, locking, partial update fieldpaths, and duplicate commits is contract-dependent and must be consistently implemented. `WithLabels` replaces label map on the mutable `Info` object rather than merging.

Test signals: the reusable `testsuite` package validates many implementations against these contracts.
