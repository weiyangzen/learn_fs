<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/sky1-power.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/sky1-power.h

### Purpose
This header defines Sky1 power-domain IDs for device-tree power-domain references.

### Important APIs, Types, And Functions
It exports 22 domain macros from `SKY1_PD_AUDIO` through `SKY1_PD_GPU`, including PCIe controller/hub, multimedia hub and SMMU, DPU0-DPU4, VPU top/cores, NPU cores/top, ISP0, and GPU.

### Control Flow
DTS preprocessing converts symbolic `SKY1_PD_*` names into integer domain cells. Runtime sequencing is handled by the Sky1 power-domain provider and generic PM domain framework.

### State, Persistence, And Dependencies
No state is stored in the header. The numeric IDs are an ABI between DTS, firmware expectations noted by the comment about Rich OS macro flow, and the Sky1 power-domain driver.

### Integration Points
Sky1 DTS nodes use these IDs in `power-domains` properties for audio, PCIe, display, video, NPU, ISP, and GPU devices.

### Risks
Incorrect IDs can power-manage the wrong hardware island, causing probe failures, hangs, or data loss for active devices. The cross-OS comment implies external consumers may depend on stable values.

### Test Signals
Build Sky1 DTBs, run power-domain binding checks, and exercise runtime PM, suspend/resume, display/media/GPU/NPU workloads, and PCIe enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/sky1-power.h -->
