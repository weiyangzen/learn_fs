## sources/control-plane/mayastor/io-engine/src/bdev/nvmf.rs

### Purpose
`nvmf.rs` implements the older SPDK bdev adapter for remote NVMe-oF targets. It parses `nvmf` URIs, connects using SPDK bdev NVMe create, attaches a single namespace, and adds the URI as a bdev alias.

### Important APIs, Types, And Functions
`Nvmf` holds controller name, alias, host, port, subsystem NQN, protection-check flags, and optional UUID. `TryFrom<&Url>` parses host/path/query. `GetName` returns `<controller>n1`. `CreateDestroy` wraps create/delete. `NvmeCreateContext` fills an NVMe TCP transport id and namespace output array.

### Control Flow
Parsing requires a host and exactly one path segment, supports `reftag`, `guard`, and `uuid`, defaults the port to 4420, and rejects unknown parameters. `create()` rejects existing namespace bdev names, constructs default controller opts and TCP transport id, calls `spdk_bdev_nvme_create()`, waits for bdev count, and deletes the partially created controller when count is zero. It then looks up `<name>n1`, checks but does not reject UUID mismatch, and adds the alias. `destroy()` deletes the NVMe controller by base name.

### State, Persistence, And Dependencies
All state is SPDK runtime state plus alias metadata. Protection-information flags are passed into the context but this file does not visibly apply `prchk_flags` to SPDK options, which is worth comparing with the newer `nvmx` path. Dependencies include SPDK NVMe bdev FFI, URI utilities, boolean/UUID parsing, `UntypedBdev`, and async callback helpers.

### Integration Points
This adapter supports generic bdev create/destroy for remote NVMe-oF targets and coexists with the newer `nvmx` implementation. Its `Probe` implementation is currently a no-op placeholder.

### Risks
UUID mismatch only logs an error and still returns success, so callers relying on UUID validation must enforce it elsewhere. `prchk_flags` in `NvmeCreateContext` appears unused. IPv6 bracket handling is absent here unlike the newer `nvmx::uri` path. The single-namespace assumption is hard-coded.

### Test Signals
Cover URI host/path validation, boolean query forms, unknown parameters, default port, UUID mismatch logging, zero namespace cleanup, create/delete callback cancellation, alias addition, and parity against `nvmx` for supported query parameters.
