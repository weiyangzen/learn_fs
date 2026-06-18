<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/gmu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/gmu.yaml

### Purpose
This binding describes Qualcomm Adreno A6xx-and-newer Graphics Management Units. GMU firmware/hardware manages GPU power and efficiency.

### Important APIs, Types, And Functions
The schema accepts versioned `qcom,adreno-gmu-*` compatibles with `qcom,adreno-gmu` fallback, x-series GMUs, and `qcom,adreno-gmu-wrapper`. It defines `reg`/`reg-names`, clocks/names, HFI and GMU interrupts, CX/GX power domains, IOMMU, `qcom,qmp`, OPP table, and wrapper-specific reduced requirements.

### Control Flow
The `allOf` chain branches by exact GMU compatible. Each branch fixes register-window names and clock lists for 615/618/630, 623, 635/660/663, 640, 650, 730/740/750/x185, 840, and x285. Non-wrapper GMUs require clocks, interrupts, IOMMU, and OPP; wrapper nodes require only wrapper register and power-domain resources.

### State, Persistence, And Dependencies
Persistent state is the GMU resource map and power-management topology. Dependencies include GPU clock controllers, CX/GX power domains, SMMU, AOSS/QMP for newer GMUs, OPP tables, interrupts, and the GPU node referencing GMU.

### Integration Points
The Adreno GPU driver uses GMU nodes to initialize firmware/HFI, vote clocks and power, and manage GPU performance states.

### Risks
Compatible-specific register/clock lists are easy to copy incorrectly between GPU generations. Missing `qcom,qmp` on newer GMUs should be caught by schema. Wrapper versus full GMU requirements differ substantially.

### Test Signals
Use binding checks per GMU generation. Runtime signals include GMU firmware boot, HFI interrupt handling, OPP transitions, CX/GX power sequencing, IOMMU setup, and GPU suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/gmu.yaml -->
