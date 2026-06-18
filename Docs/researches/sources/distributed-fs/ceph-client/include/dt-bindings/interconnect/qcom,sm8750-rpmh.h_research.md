<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8750-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8750-rpmh.h

## Purpose
This header provides SM8750 RPMh interconnect node identifiers for device tree. It represents newer SM8750 fabrics including SOCCP, EVA/video, UBWC, PCIe, multimedia, compute, memory, and system NOC endpoints.

## Important APIs, types, and functions
Only macros are exported. Important families include A1NOC/A2NOC IDs, `MASTER_SOCCP_AGGR_NOC`, `SLAVE_SOCCP`, CNOC config slaves, `MASTER_UBWC_P`, `SLAVE_UBWC_P`, `MASTER_VIDEO_EVA`, `MASTER_VIDEO_MVP`, `MASTER_CAMNOC_*`, `MASTER_PCIE_0`, and SNOC/GEM_NOC endpoints.

## Control flow
The macros are expanded during DTS preprocessing and become numeric cells in interconnect paths. The SM8750 interconnect provider later interprets them while building ICC paths and sending RPMh votes.

## State and persistence
The file has no state or persistence logic. Its constants become persistent DT ABI once DTBs are distributed.

## Dependencies and integration points
It depends on the matching Qualcomm SM8750 ICC provider implementation and device-tree schemas. Integration points include camera, EVA/video, display, PCIe, USB/storage, GPU, modem, SPSS, and system configuration nodes.

## Risks and test signals
Risks include introducing a new endpoint macro without a provider table entry, using an SM8650 ID on SM8750 DTS, and renumbering existing IDs. Test signals include DTS preprocessing, schema validation, ICC provider probe, and functional bandwidth votes for camera/video/display stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8750-rpmh.h -->
