<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adi-axi-common.h -->
# sources/distributed-fs/ceph-client/include/linux/adi-axi-common.h

## Purpose
`adi-axi-common.h` defines common register offsets and version/FPGA metadata helpers for Analog Devices AXI FPGA IP cores.

## Important APIs, types, and functions
Register offsets include `ADI_AXI_REG_VERSION` and `ADI_AXI_REG_FPGA_INFO`. Version macros pack and unpack semantic major/minor/patch fields. `adi_axi_pcore_ver_gteq()` checks whether a hardware version is at least a required major/minor pair. FPGA info macros decode technology, family, and speed-grade fields. Enums define known FPGA technology, family, and speed-grade values.

## Control flow
Drivers read version/info registers from hardware, decode fields with macros, and gate features using `adi_axi_pcore_ver_gteq()`.

## State and persistence behavior
The header stores no state. It interprets persistent hardware register values.

## Dependencies and integration points
It depends on Linux integer types and is shared by ADI AXI IP drivers that need consistent register decoding.

## Risks and test signals
Risks include version comparison ignoring patch-level requirements, misdecoded bitfields, and assuming unknown enum values cannot occur. Test signals include unit tests for macro packing/unpacking, driver probes across IP versions, and feature-gating tests for boundary versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adi-axi-common.h -->
