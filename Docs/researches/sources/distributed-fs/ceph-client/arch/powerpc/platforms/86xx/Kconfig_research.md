# sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Kconfig

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Kconfig -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Kconfig

### Purpose
Kconfig menu for Freescale 86xx platforms. It defines the platform family and board selections that control compilation of the 86xx board support files.

### Important APIs, Types, And Functions
Key symbols include `PPC_86xx` and board options for MPC8641 HPCN, GE PPC9A/SBC310/SBC610, MVME7100, and related 86xx support. The symbols select dependencies such as MPIC, FSL PCI, default CPU family, and board-specific options.

### Control Flow
No runtime flow. Kconfig choices drive Makefile object inclusion and architecture features at build time.

### State, Persistence, And Dependencies
State is build configuration only. Dependencies are Kconfig relationships, selected architecture features, and downstream Makefile rules.

### Integration Points
Controls whether `arch/powerpc/platforms/86xx` objects are built and which machine descriptors are available to the kernel.

### Risks
Incorrect select/depends relationships can build incomplete platform support or expose options on incompatible CPU families.

### Test Signals
Run olddefconfig/menuconfig for each 86xx board, verify expected objects compile, and confirm generated configs include MPIC/FSL PCI features when needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/Kconfig -->
