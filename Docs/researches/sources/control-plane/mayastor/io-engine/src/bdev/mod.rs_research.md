<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/mod.rs

Purpose: Public module facade and shared traits for io-engine block-device implementations.

Important APIs/types: re-exports generic device operations, `SpdkBlockDevice`, nexus types, and NVMe controller state. Declares internal modules for aio, dev, device, ftl, loopback, lvs, malloc, null, nvme, nvmf/nvmx, nexus, uring, and util. Defines `BdevCreateDestroy` as the combined trait of `CreateDestroy`, `Probe`, `GetName`, and `Debug`; `CreateDestroy` provides async create/destroy; `GetName` returns device name; `Probe` validates device availability with default `UriNotHandled`; `ProbeOpts` carries import/create context. Helper functions create `ProbeError`, probe files, probe existing bdevs, and recursively probe URIs. `PtplFileOps` abstracts reservation persistence file paths.

State and dependencies: `PtplFileOps` reads global `MayastorEnvironment` for PTPL directory and creates/deletes files as implemented by resources. Probe helpers inspect filesystem or SPDK bdev registry.

Risks and test signals: trait contracts are central to adding new bdev schemes. Probe defaults to unsupported unless implemented. Validate new modules by dispatcher parsing, probe behavior, create/destroy lifecycle, and PTPL path handling.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/mod.rs -->
