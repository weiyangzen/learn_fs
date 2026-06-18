# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctdaio.h

Purpose: public Digital Audio I/O resource interface for ctxfi.

Important APIs and types: `enum DAIOTYP` enumerates line outputs, S/PDIF out/in, line input, dedicated mic, RCA, and bay S/PDIF. `struct daio`, `struct dao`, `struct dai`, descriptors `dao_desc`/`daio_desc`, operation tables `dao_rsc_ops`/`dai_rsc_ops`, and `struct daio_mgr` define DAIO allocation, enable/disable, mapper management, and commits.

Control flow and integration: ATC creates the manager, requests persistent endpoint resources, then DAO/DAI ops connect those endpoints to mixer/SRC resources. The manager bridges high-level resource graphs to hardware DAIO control blocks.

State and persistence: describes transient runtime resources, imapper list state, and per-endpoint control blocks. No independent persistence.

Risks and test signals: `type`, `msr`, `passthru`, and `output` are bitfields; callers must initialize descriptors carefully. Test compile-time consumers and runtime allocation paths for all enum values valid on each chip.
