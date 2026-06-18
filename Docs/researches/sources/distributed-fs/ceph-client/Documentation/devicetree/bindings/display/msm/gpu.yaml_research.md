<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/gpu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/gpu.yaml

### Purpose
This schema defines Qualcomm Adreno and older AMD Imageon GPU nodes. It is selected for `qcom,adreno` or `amd,imageon` compatible strings.

### Important APIs, Types, And Functions
The binding API includes compatible patterns that encode chip ID or GPU/patch level, clocks/names, register windows, one interrupt, interconnects, IOMMU streams, SRAM/OCMEM phandles, OPP table, one power domain, optional `zap-shader` child with memory-region and firmware name, cooling cells, nvmem efuse cells, and optional `qcom,gmu`.

### Control Flow
The `allOf` chain branches by compatible regex to enforce generation-specific clock counts and names across a3xx, a4xx, a5xx, a6xx, and newer parts. GMU-attached devices use `qcom,gmu` to delegate power management to the GMU node.

### State, Persistence, And Dependencies
Persistent state describes GPU resources, memory address translation, interconnect bandwidth paths, firmware memory, thermal cooling interface, and optional GMU linkage. Dependencies include clock controllers, SMMU, interconnect providers, power domains, reserved memory, nvmem, OPP tables, and GMU binding.

### Integration Points
The msm/adreno DRM driver consumes this node for GPU probe, memory management, firmware loading, performance scaling, thermal integration, and GMU-managed power on newer devices.

### Risks
Regex-compatible parsing means string accuracy is important; wrong patch levels can select wrong driver data. IOMMU list cardinality is broad, so semantic stream-ID errors may only appear as faults. Zap shader memory must match firmware expectations.

### Test Signals
Validate with `dt_binding_check` for representative GPU generations. Runtime signals include GPU probe, ring submission, IOMMU fault absence, OPP/interconnect scaling, GMU link operation, zap shader load, and thermal cooling registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/display/msm/gpu.yaml -->
