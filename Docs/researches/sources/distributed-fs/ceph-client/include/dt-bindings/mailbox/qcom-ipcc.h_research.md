<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/qcom-ipcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/qcom-ipcc.h

## Purpose
This header defines Qualcomm IPCC mailbox client IDs and MPROC signal IDs for device-tree mailbox specifiers.

## Important APIs, types, and functions
It exports signal IDs `IPCC_MPROC_SIGNAL_GLINK_QMP`, `TZ`, `SMP2P`, and `PING`, plus client IDs including `IPCC_CLIENT_AOP`, `TZ`, `MPSS`, `LPASS`, `SLPI`, `CDSP`, `APSS`, `GPU`, `CAM`, `PCIE0..2`, `SPSS`, `NSP1`, `TME`, `WPSS`, and `GPDSP0/1`.

## Control flow
Qualcomm DTS mailbox users encode remote client and signal IDs with these macros. The IPCC mailbox driver translates the DT cells into register offsets/bits for interrupting or receiving notifications from remote processors.

## State and persistence
The header is stateless. Mailbox routing state is hardware/runtime state; IDs in DTBs are stable firmware-facing configuration.

## Dependencies and integration points
It integrates with Qualcomm IPCC, GLINK/QMP, TrustZone, SMP2P, remoteproc subsystems, AOP/CDSP/SLPI/MPSS/LPASS clients, and PCIe or multimedia remote agents.

## Risks and test signals
Risks include client ID gaps, using a client unsupported on a specific SoC, and mixing signal IDs across protocols. Test signals include `dtbs_check`, IPCC mailbox probe, remoteproc boot, SMP2P/GLINK communication, and interrupt delivery between APSS and remote clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/qcom-ipcc.h -->
