# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lan_pf_regs.h

## Purpose
`idpf_lan_pf_regs.h` defines the PF-side LAN register offsets and bit masks used by the IDPF driver. It covers queue tail doorbells, PF firmware mailbox rings, PTP command synchronization, interrupt dynamic control and ITR registers, miscellaneous interrupt cause registers, PCI function RID decoding, and PF reset trigger/status/control registers.

## Important APIs, types, and functions
- RX/TX queue registers: `PF_QRX_TAIL()`, `PF_QRX_BUFFQ_TAIL()`, and `PF_QTX_COMM_DBELL()`.
- PF mailbox: `PF_FW_ARQ*` and `PF_FW_ATQ*` base address, length, head, tail, overflow, critical, and enable masks.
- PTP command bits: `PF_GLTSYN_CMD_SYNC_EXEC_CMD_M` and `PF_GLTSYN_CMD_SYNC_SHTIME_EN_M`.
- Interrupts: `PF_GLINT_DYN_CTL()`, `PF_GLINT_ITR()`, `PF_GLINT_ITR_ADDR()`, `PF_GLINT_ITR_MAX_INDEX`, and `PF_GLINT_ITR_INTERVAL_M`.
- Other interrupt and identity registers: `PF_INT_DIR_OICR_*`, `PF_INT_PBA_CLEAR`, and `PF_FUNC_RID_*`.
- Reset registers: `PFGEN_RTRIG`, `PFGEN_RSTAT`, `PFGEN_CTRL`, and related bit masks.

## Control flow
This header has no runtime control flow. Device-specific register initialization code includes these constants to populate `idpf_reg_ops` register descriptors. Later code uses the resulting MMIO pointers for mailbox setup, interrupt enable/disable, queue tail writes, reset polling, and PTP direct clock command synchronization.

## State and persistence behavior
The definitions describe hardware state in BAR0. Writes to queue tail and TX common doorbell registers advance hardware producer indices. Mailbox length/head/tail registers define the control queue state. Dynamic interrupt and ITR registers control interrupt enablement and moderation. Reset registers trigger and report PF resets. The header itself stores no software state.

## Dependencies and integration points
The header relies on Linux `BIT` and `GENMASK` style macros provided by included driver context. It is paired with PF device ops setup and used indirectly by `idpf_main.c` hardware mapping, `idpf_lib.c` mailbox/interrupt/reset flows, and `idpf_ptp.c` direct PTP command reads when PF PTP registers are initialized.

## Risks and edge cases
- Register offsets and masks are hardware ABI. Any incorrect value can corrupt unrelated register programming or break reset/interrupt/mailbox operation.
- PF and VF register spacing differs substantially; using PF macros for VF devices would misprogram BAR offsets.
- ITR spacing helper arguments must match the selected hardware generation.
- Reset masks must align with firmware readiness semantics; otherwise reset completion polling can falsely pass or time out.

## Test signals
Validation comes from PF probe, mailbox initialization and virtchnl traffic, queue bring-up with correct tail writes, MSI-X interrupt delivery and moderation changes, PTP direct clock access on capable PFs, function reset trigger/recovery, and register trace comparison against hardware specifications.
