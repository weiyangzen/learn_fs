## sources/distributed-fs/ceph-client/drivers/dma/amd/qdma/Makefile

### Purpose
This Makefile builds the AMD QDMA driver object from the core QDMA implementation and shared register-definition file.

### Important APIs, Types, And Functions
It creates `amd-qdma.o` when `CONFIG_AMD_QDMA` is enabled and composes it from `qdma.o` and `qdma-comm-regs.o`.

### Control Flow, State, And Persistence
No runtime state exists. The Makefile ensures the register offset/field tables are linked into the QDMA driver module with the core implementation.

### Dependencies, Integration Points, Risks, And Test Signals
The file must match the `AMD_QDMA` Kconfig symbol and source filenames. Risks include missing register table linkage if object names change and redundant `-$(CONFIG_AMD_QDMA)` conditional inside a directory only reached for the same config. Test signals include successful `amd-qdma` module link and symbol resolution for `qdma_regos_default` and `qdma_regfs_default`.
