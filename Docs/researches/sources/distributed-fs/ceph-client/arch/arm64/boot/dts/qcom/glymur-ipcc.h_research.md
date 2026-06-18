# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/glymur-ipcc.h

## Purpose
This Qualcomm binding header defines IPCC mailbox client and signal IDs for the Glymur platform. DTS mailbox specifiers use these constants to address remote processors and interrupt channels.

## APIs, Types, And Constants
The macro API is split into physical client IDs (`IPCC_MPROC_*`), compute low-power level IDs (`IPCC_COMPUTE_L0_*`, `IPCC_COMPUTE_L1_*`), and peripheral IDs (`IPCC_PERIPH_*`). It covers AOP, TZ, modem, LPASS, SLPI, SDC, CDSP, NPU, APSS, GPU, PCIe instances, SPSS, TME, WPSS, SOCCP, and media/display units.

## Control Flow And State
There is no executable flow or state. Constants become numeric mailbox cells in DTBs and are interpreted by Qualcomm IPCC/mailbox-related drivers.

## Dependencies And Integration
The header has only include guards and no includes. It integrates with Glymur DTS files and the Qualcomm IPCC binding, where client and signal IDs must match firmware/hardware routing tables.

## Risks And Test Signals
Risks are ABI mismatches against firmware, duplicate or wrong numeric IDs, and confusing platform-specific IDs with another SoC. Tests are DTB compilation, mailbox driver probe, remoteproc bring-up, and functional IPC between APSS and remote processors.
