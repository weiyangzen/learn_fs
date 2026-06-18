<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,x1e80100-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,x1e80100-rpmh.h

## Purpose
This binding header defines RPMh interconnect IDs for Qualcomm X1E80100. It covers laptop-class fabrics including multiple PCIe and USB/USB4 aggregators, QUP, CNOC, GEM_NOC, MC/LLCC, multimedia, CDSP, LPASS, and SNOC paths.

## Important APIs, types, and functions
The API is the macro set. Notable endpoints include `MASTER_DDR_PERF_MODE`, `SLAVE_DDR_PERF_MODE`, `MASTER_PCIE_TCU`, `MASTER_GIC1`, `MASTER_GIC2`, `MASTER_PCIE_NORTH`, `MASTER_PCIE_SOUTH`, `MASTER_AGGRE_USB_NORTH`, `MASTER_AGGRE_USB_SOUTH`, `MASTER_USB4_0..2`, and `SLAVE_AGGRE_USB_*`.

## Control flow
DTS files include this header and emit numeric IDs in interconnect specifiers. During boot, the X1E80100 ICC provider maps those IDs to driver-side nodes for RPMh bandwidth voting and aggregate path management.

## State and persistence
No runtime state exists in this header. Values embedded into DTBs are stable platform ABI.

## Dependencies and integration points
It integrates with Qualcomm ICC/RPMh, device-tree schemas, and platform devices for PCIe, USB2/USB3/USB4, UFS, SDCC, QUP, display, camera, video, GPU, CDSP, LPASS, and memory controllers.

## Risks and test signals
Risks include PCIe north/south or USB north/south ID confusion, drift from provider table ordering, and endpoint omissions for high-speed laptop I/O. Test signals are `dtbs_check`, X1E80100 ICC provider probe, PCIe and USB4 throughput tests with nonzero ICC votes, and display/camera bandwidth validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,x1e80100-rpmh.h -->
