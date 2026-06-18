<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8650-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8650-rpmh.h

## Purpose
This header defines SM8650 RPMh interconnect node IDs. It covers the SoC's A1NOC/A2NOC, QUP core, CNOC config, GEM_NOC, MC/LLCC, multimedia, CDSP, PCIe ANOC, and SNOC domains for device-tree bandwidth paths.

## Important APIs, types, and functions
The exported surface is macro constants such as `MASTER_QUP_3`, `SLAVE_I3C_IBI0_CFG`, `MASTER_UBWC_P_TCU`, `MASTER_UBWC_P`, `MASTER_GIC`, `MASTER_APSS_NOC`, and common storage/display/camera/video/PCIe endpoints. There are no callable functions.

## Control flow
Device-tree sources include the header and pass these numeric IDs to `interconnects` properties. The compiled DTB feeds those IDs to the SM8650 Qualcomm ICC provider, which maps them to NOC nodes and issues RPMh aggregate bandwidth requests.

## State and persistence
No state is stored here. The macro values are persistent firmware-facing ABI values once included in DTBs.

## Dependencies and integration points
The header must match SM8650 ICC driver node arrays and YAML binding expectations. It is consumed by DTS nodes for QUP/I3C/I2C, UFS, SDCC, USB, PCIe, GPU, display, camera, video, CDSP, modem, and system fabric clients.

## Risks and test signals
Risks include SM8550/SM8750 copy-paste drift, mismatched `MASTER_QUP_*` and `SLAVE_QUP_*` numbering, and missing new SM8650 endpoints in provider data. Test signals are `dtbs_check`, `make dt_binding_check` for Qualcomm ICC bindings, successful driver probe, and runtime bandwidth voting for high-traffic multimedia and storage paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8650-rpmh.h -->
