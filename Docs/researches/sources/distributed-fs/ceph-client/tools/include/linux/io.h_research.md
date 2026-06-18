<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/io.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/io.h

## Purpose
`io.h` forwards tools code to architecture-specific I/O accessor definitions.

## APIs And Flow
It includes `<asm/io.h>` and defines no extra helpers. Any `read*`, `write*`, `ioremap`-like, or port I/O semantics come from the selected tools architecture header.

## State, Dependencies, Risks, Tests
There is no state here. The dependency and integration point is the architecture include path. The risk is that this tools header lacks the rich kernel `linux/io.h` managed mapping API, so consumers must only rely on symbols supplied by `asm/io.h`. Test signals are per-architecture tool builds and compile coverage for any accessor used by perf or other tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/io.h -->
