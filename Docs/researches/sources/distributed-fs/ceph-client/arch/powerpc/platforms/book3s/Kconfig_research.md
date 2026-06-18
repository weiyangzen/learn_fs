# sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Kconfig

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Kconfig -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Kconfig

### Purpose
Book3S platform feature Kconfig, currently focused on the Virtual Accelerator Switchboard user API.

### Important APIs, Types, And Functions
Defines `PPC_VAS`, which enables VAS support for user and kernel access to POWER accelerator functions such as NX compression.

### Control Flow
No runtime flow. The symbol controls compilation of `vas-api.o` and related VAS infrastructure.

### State, Persistence, And Dependencies
State is build configuration. Dependencies include Book3S platform capability and VAS/NX support.

### Integration Points
Controls whether the Book3S VAS character-device API is available to accelerator drivers.

### Risks
Incorrect dependency gating could expose VAS APIs on systems without hardware or omit them from systems needing NX acceleration.

### Test Signals
Build Book3S configs with and without `PPC_VAS`, verify object inclusion and dependent accelerator drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/book3s/Kconfig -->
