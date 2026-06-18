# sources/distributed-fs/ceph-client/include/dt-bindings/firmware/qcom,scm.h

## Purpose
Defines Qualcomm SCM VMID constants for secure monitor and memory ownership bindings.

## Important APIs, Types, and Constants
Exports `QCOM_SCM_VMID_*` macros for trust zone, HLOS, sensor/ADSP/CDSP/MDSP subsystems, secure display/camera/video, hypervisor, WLAN, SPSS, NAV, TVM, and OEMVM IDs. Values are sparse hexadecimal VM identifiers from `0x1` through `0x31`.

## Control Flow and State
No local flow. Runtime state is in Qualcomm secure firmware/hypervisor memory protection tables; these IDs identify VM owners in SCM calls or DT properties.

## Dependencies and Integration Points
Self-contained binding used by Qualcomm firmware, memory protection, reserved-memory, and SCM-related DT descriptions.

## Risks and Test Signals
Wrong VMID values are security-sensitive and can assign memory or device access to the wrong execution environment. Test signals include DT schema validation, SCM call success, memory assignment tests, and secure subsystem boot validation.
