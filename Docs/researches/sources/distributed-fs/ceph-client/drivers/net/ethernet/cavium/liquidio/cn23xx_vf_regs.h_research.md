# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn23xx_vf_regs.h

## Purpose
This header defines the VF-visible CN23XX PCI config offsets, queue CSR offsets, mailbox signal registers, interrupt bits, PTP/MIO registers, reset boot register, and MSI-X table layout.

## Important APIs, Types, And Functions
Important macros include `CN23XX_VF_SLI_IQ_*` and `CN23XX_VF_SLI_OQ_*` for queue programming, shared input/output control bit masks, `CN23XX_VF_SLI_PKT_MBOX_INT()` and `CN23XX_SLI_PKT_PF_VF_MBOX_SIG()` for VF mailbox communication, `CN23XX_VF_SLI_INT_SUM()` for per-queue interrupt summary, PTP register constants, and MSI-X table macros.

## Control Flow
There is no executable flow. `cn23xx_vf_device.c` uses the macros to reset queues, set descriptor ring bases, control queue enable bits, configure interrupt thresholds, and exchange mailbox messages with the PF.

## State And Persistence
State lives in hardware registers addressed by these macros. The header itself has no persistence.

## Dependencies And Integration Points
The header depends on `BIT`/`BIT_ULL` availability and is included through `cn23xx_vf_device.h`. It mirrors selected PF register definitions with VF-relative names and read-only comments for PF/VF identity fields.

## Risks
PF and VF headers duplicate many masks; divergence can break handshake and queue programming. Endian-dependent masks must match the PF and hardware. The header exposes PTP registers but the VF code read here does not directly use them, so unused definitions may drift.

## Test Signals
Compile VF builds on little- and big-endian configurations, verify register offsets against CN23XX VF hardware docs, and exercise queue, mailbox, interrupt, and MSI-X table accesses in VF probe and traffic tests.
