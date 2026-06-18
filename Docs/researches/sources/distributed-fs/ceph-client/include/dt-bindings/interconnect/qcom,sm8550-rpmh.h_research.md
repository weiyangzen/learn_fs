<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8550-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8550-rpmh.h

## Purpose
This binding header assigns stable integer node IDs for the Qualcomm SM8550 RPMh interconnect provider. It gives DTS authors symbolic names for A1NOC, A2NOC, QUP core, CNOC, GEM_NOC, MC/LLCC, MNOC, CDSP, PCIe ANOC, and SNOC master/slave endpoints.

## Important APIs, types, and functions
The public API is the macro namespace: `MASTER_*` and `SLAVE_*` IDs such as `MASTER_QSPI_0`, `MASTER_UFS_MEM`, `SLAVE_A1NOC_SNOC`, `MASTER_GPU_TCU`, `SLAVE_LLCC`, `MASTER_CAMNOC_HF`, and `SLAVE_EBI1`. There are no C types or functions.

## Control flow
DTS files include the header, then use these constants in interconnect specifier cells. At build time the C preprocessor replaces names with integers; at runtime the Qualcomm ICC driver resolves those IDs against the SM8550 provider tables for bandwidth voting through RPMh.

## State and persistence
The header has no runtime state. Its numbers are ABI-like device-tree data and must remain stable for compiled DTBs that reference them.

## Dependencies and integration points
It integrates with Qualcomm interconnect bindings, the SM8550 interconnect driver data, RPMh bandwidth voting, and DT nodes for display, camera, video, storage, USB, PCIe, GPU, modem, compute DSP, LPASS, and debug clients.

## Risks and test signals
Risks include duplicate IDs inside one provider domain, DTS using an endpoint that the driver table does not expose, and accidental renumbering that breaks existing DTBs. Test signals are `dtbs_check`, successful preprocessing of SM8550 DTS includes, driver probe without unknown-node warnings, and bandwidth votes observed for UFS, USB, display, camera, and PCIe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8550-rpmh.h -->
