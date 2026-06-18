# sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Kconfig

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Kconfig -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Kconfig

### Purpose
Kconfig definitions for MPC8xx/PQ1 platforms and board options.

### Important APIs, Types, And Functions
Symbols define `PPC_8xx` platform support and boards such as MPC86xADS, MPC885ADS, TQM8xx, EP88xC, and Adder875. It also exposes feature options for CPM1, 8xx GPIO, device tree, and board-specific support.

### Control Flow
No runtime flow. Kconfig selects CPU family, interrupt, CPM, and board object build coverage.

### State, Persistence, And Dependencies
State is build configuration. Dependencies are Kconfig expressions, default selections, and Makefile object rules.

### Integration Points
Controls compilation of `arch/powerpc/platforms/8xx` machine, PIC, CPM1, and board setup files.

### Risks
Incorrect selects can build boards without required CPM/PIC support or hide valid board options.

### Test Signals
Generate configs for each 8xx board, verify expected symbols and objects, and build with/without optional GPIO and CPM features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/8xx/Kconfig -->
