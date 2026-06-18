# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lan_vf_regs.h

## Purpose
`idpf_lan_vf_regs.h` defines VF-side LAN BAR register offsets and masks. It covers VF reset status, admin transmit/receive queue mailbox registers, queue tail doorbells, interrupt dynamic control and ITR layouts for multiple VF vector scaling modes, interrupt cause registers, and VF RSS key/LUT/HENA registers.

## Important APIs, types, and functions
- Reset: `VFGEN_RSTAT` and `VFGEN_RSTAT_VFR_STATE_M`.
- VF mailbox: `VF_ATQ*` and `VF_ARQ*` length, head, tail, overflow, critical, and enable fields.
- Queue tails: `VF_QTX_TAIL()`, `VF_QTX_TAIL_EXT()`, `VF_QRX_TAIL()`, `VF_QRX_TAIL_EXT()`, and `VF_QRXB_TAIL()`.
- Interrupt control: `VF_INT_DYN_CTL0`, `VF_INT_DYN_CTLN()`, `VF_INT_DYN_CTLN_EXT()`, `VF_INT_ITR0()`, `VF_INT_ITRN()`, `VF_INT_ITRN_64()`, `VF_INT_ITRN_2K()`, and `VF_INT_ITRN_ADDR()`.
- Mailbox interrupt cause: `VF_INT_ICR0_ENA1`, `VF_INT_ICR01`, and admin queue mask bits.
- RSS registers: `VF_QF_HENA()`, `VF_QF_HKEY()`, and `VF_QF_HLUT()`.

## Control flow
This header has no runtime control flow. VF device ops use it to initialize register tables and MMIO offsets. Probe-time device-type detection in `idpf_main.c` writes to `VF_ARQBAL` to distinguish VF from PF when the PCI class entry is generic.

## State and persistence behavior
The macros describe VF-visible hardware state. Mailbox registers control admin queue DMA rings, queue tail registers notify hardware of new TX/RX descriptors, interrupt registers enable and moderate MSI-X delivery, reset status reports VF reset progress, and QF RSS registers hold VF RSS programming when direct VF access is used. The file stores no software state.

## Dependencies and integration points
The header depends on bit-mask macros and is included by `idpf_main.c` for VF detection. It is also consumed by VF register ops initialization code in the driver, mailbox setup, interrupt code, queue register initialization, and RSS configuration paths.

## Risks and edge cases
- The VF register layout has several vector-count-dependent ITR formulas. Selecting the wrong formula for a device capability can direct ITR writes to the wrong register.
- Queue tail EXT and non-EXT offsets differ; incorrect choice can break queue progress.
- VF mailbox register order is not monotonic by name, so assumptions based on PF layout are unsafe.
- Probe's write/read VF test relies on `VF_ARQBAL` being writable for VFs and not behaving the same way for PFs; hardware changes could affect detection.

## Test signals
Validation includes VF probe through both explicit VF ID and generic class ID, successful admin queue negotiation, VF reset detection, TX/RX queue progress through tail writes, mailbox interrupt delivery, interrupt moderation changes across 16/64/2k vector layouts, and direct RSS programming where applicable.
