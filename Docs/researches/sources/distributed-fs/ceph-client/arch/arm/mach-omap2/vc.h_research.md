<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc.h

### Purpose
`vc.h` defines the OMAP Voltage Controller register metadata, per-channel state, channel flags, exported SoC data objects, and VC operation prototypes.

### Important APIs, Types, And Functions
Core types are `struct omap_vc_common` and `struct omap_vc_channel`. Flags include `OMAP_VC_CHANNEL_DEFAULT` and `OMAP_VC_CHANNEL_CFG_MUTANT`. It declares OMAP3/4 VC channel and parameter objects plus VC init and scaling APIs.

### Control Flow
There is no executable flow. The structures describe how generic VC code writes SoC-specific registers and fields.

### State, Persistence, And Dependencies
State lives in instances declared here and defined in VC data files. It depends on `struct voltagedomain` and shared voltage parameter types from `voltage.h`.

### Integration Points
Voltage-domain data points to these VC channel instances, and `vc.c` uses their masks, offsets, and shifts to program PRM registers.

### Risks
Incorrect bit shifts or flags can corrupt unrelated PRM fields. The header documents that some fields are redundant or awkwardly represented, so future changes need careful compatibility review.

### Test Signals
Build coverage across OMAP3/4 validates object declarations; runtime register programming tests validate masks and shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vc.h -->
