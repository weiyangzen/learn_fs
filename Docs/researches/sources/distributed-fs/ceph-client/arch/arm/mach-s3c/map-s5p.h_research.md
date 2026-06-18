<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s5p.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s5p.h

### Purpose
Provides S5P-family mapping aliases needed by shared Samsung ARM code.

### Important APIs, Types, And Functions
It includes common map base definitions and defines S5P virtual address aliases used by register headers and early machine code.

### Control Flow
No runtime flow.

### State, Persistence, And Dependencies
No state. It depends on the shared Samsung map base.

### Integration Points
Used by older S5P code paths that share S3C-style address macros.

### Risks
Mixing S3C and S5P aliases can obscure which SoC address map is active.

### Test Signals
Compile coverage and early S5P boot mapping validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s3c/map-s5p.h -->
