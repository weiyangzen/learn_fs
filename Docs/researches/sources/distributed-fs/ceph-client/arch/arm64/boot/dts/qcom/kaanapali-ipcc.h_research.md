# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kaanapali-ipcc.h

## Purpose
This binding header defines Qualcomm Kaanapali platform IPCC mailbox identifiers for use in device-tree mailbox specifiers.

## APIs, Types, And Constants
It exports physical client IDs such as `IPCC_MPROC_AOP`, `TZ`, `MPSS`, `LPASS`, `SDC`, `CDSP`, `APSS`, `SOCCP`, `DCP`, `SPSS`, `TME`, and `WPSS`. It also defines compute L0/L1 IDs, peripheral IDs for CDSP/APSS/PCIe, and fence IDs for CDSP, APSS, GPU, CVP, camera, DCP, VPU, and SOCCP.

## Control Flow And State
The file is declarative. Numeric constants are expanded into DTBs and consumed at runtime by mailbox/IPCC drivers and remote processor integrations.

## Dependencies And Integration
There are no includes. The integration contract is the Kaanapali firmware and hardware IPCC routing table. DTS files must include this platform-specific header rather than reusing IDs from related Qualcomm SoCs.

## Risks And Test Signals
Risks include duplicate aliases with different meanings, wrong fence IDs, and mismatched values across firmware revisions. Build tests only validate preprocessing; runtime signals are successful mailbox probe, remoteproc startup, and IPC/fence operations without timeout errors.
