# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_register.h

## Purpose
Defines the VF-visible MMIO register offsets and bit masks used by the IAVF driver. These are the low-level hardware ABI for AdminQ rings, reset status, interrupt control, queue tails, RSS tables, and interrupt throttling registers.

## Important APIs, Types, and Functions
This file is macro-only. Key register families are `IAVF_VF_ARQ*` and `IAVF_VF_ATQ*` for Admin Receive/Transmit Queue base, head, tail, and length registers; `IAVF_VFGEN_RSTAT` for VF reset state; `IAVF_VFINT_DYN_CTL*`, `IAVF_VFINT_ICR*`, and `IAVF_VFINT_ITRN1` for interrupt control and ITR programming; `IAVF_QRX_TAIL1` and `IAVF_QTX_TAIL1` for Rx/Tx queue tails; and `IAVF_VFQF_HENA/HKEY/HLUT` for RSS hash enable, key, and lookup table registers.

## Control Flow
The header has no executable control flow. Other driver files compose these offsets with `rd32`, `wr32`, or `writel` operations. For example, `iavf_txrx.c` writes `IAVF_VFINT_DYN_CTLN1` to re-enable interrupts and force writebacks, and uses queue tail pointers derived from these register definitions.

## State and Persistence
State is hardware-resident: AdminQ indices and enable bits, interrupt enable/mask/ITR settings, queue tail producer indices, RSS key/LUT/hash enable registers, and reset status. The software persistence is only the set of constants compiled into the module.

## Dependencies and Integration Points
Uses `IAVF_MASK` from `iavf_type.h`. It is included by `iavf_type.h` and consequently reaches the AdminQ, interrupt, queue setup, RSS, and Tx/Rx paths. It must stay in sync with Intel VF hardware documentation and with PF/virtchnl expectations.

## Risks
Any incorrect offset or mask can break DMA queue operation, AdminQ communication, interrupt moderation, or RSS programming. Some indexed macros document limited hardware ranges, so callers must validate queue/vector indices elsewhere. Register reset-domain comments are informative but not enforced.

## Test Signals
Signals include successful VF probe and AdminQ initialization, queue enable/disable traffic tests, MSI-X interrupt delivery, adaptive ITR changes visible in interrupt rate behavior, RSS hash/LUT programming via ethtool, reset recovery, and register dumps matching expected VF offsets.
