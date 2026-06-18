# sources/distributed-fs/ceph-client/arch/arm64/include/asm/numa.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/numa.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/numa.h

### Purpose
`numa.h` connects ARM64 topology definitions to the generic NUMA interface.

### Important APIs, Types, And Functions
It includes `asm/topology.h` and `asm-generic/numa.h`; it has no additional ARM64-specific API surface in this file.

### Control Flow
Generic NUMA initialization and memory policy code use the included definitions. This header itself has no runtime flow.

### State, Persistence, And Dependencies
NUMA state lives in generic node, distance, and memory topology data. Dependencies are ARM64 topology parsing and generic NUMA code.

### Integration Points
Affects page allocation locality for page cache, networking, block I/O, and Ceph client memory.

### Risks
The risk is include/API drift; real NUMA behavior is in the included topology/generic files.

### Test Signals
Boot NUMA ARM64 systems, inspect node topology, run memory policy and page allocation locality tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/numa.h -->
