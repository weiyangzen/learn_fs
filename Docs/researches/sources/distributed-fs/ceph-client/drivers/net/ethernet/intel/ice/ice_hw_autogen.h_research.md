# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_hw_autogen.h

## Purpose
Machine-generated register map header for the `ice` hardware family. It provides register addresses, indexed register address formulas, bit positions, and bit masks used by AdminQ, mailbox, interrupt, queue, reset, flow director, statistics, PTP/timestamping, power-management, and E830-specific code.

## Important APIs, types, and functions
This header defines macros rather than functions. Major groups include:
- Firmware/AdminQ and mailbox rings: `PF_FW_*`, `PF_MBX_*`, `PF_SB_*`, and `VF_MBX_*`.
- DCB and parser/flex descriptor registers: `PRTDCB_*`, `GLFLXP_*`, `QRXFLXP_CNTXT`.
- Reset and function control: `GLGEN_*`, `PFGEN_*`, `VFGEN_*`, `VPGEN_*`.
- Interrupt programming: `GLINT_*`, `PFINT_*`, `QINT_*`, `VPINT_*`, `VFINT_DYN_CTLN`.
- Queue allocation and queue control: `PFLAN_TX_QALLOC`, `QRX_*`, `VPLAN_*`, `GLCOMM_QTX_*`.
- Malicious-driver detection: `GL_MDET_*`, `PF_MDET_*`, `VP_MDET_*`.
- NVM management: `GLNVM_*`, `GL_MNG_FWSM`.
- Flow director and hash/filter registers: `GLQF_*`, `PFQF_*`, `VSIQF_*`.
- Port/VSI/VF statistics: `GLPRT_*`, `GLV_*`, `GLSTAT_*`.
- PTP and timestamping: `GLTSYN_*`, `E830_GLTSYN_*`, `E830_PRTTSYN_*`, semaphores `PFTSYN_SEM` and `E830_PFPTM_SEM`.
- Power management and wake events: `PFPM_*`.

## Control flow
There is no executable control flow. The macros are expanded by low-level register accessors such as `rd32()` and `wr32()` throughout the driver. Indexed macros compute MMIO offsets from queue, vector, VF, VSI, profile, or timer indices.

## State and persistence behavior
No in-memory state is stored here. The definitions describe device MMIO state that persists according to hardware reset domains. Many masks correspond to hardware latches or enable bits that must be cleared or programmed by other modules.

## Dependencies and integration points
Depends on common bit helpers such as `BIT`, `GENMASK`, and `ICE_M`. It is included through the broader hardware headers and used by `ice_main.c`, `ice_txrx.c`, `ice_sriov.c`, `ice_ptp.c`, `ice_ptp_hw.c`, `ice_ethtool.c`, and queue/interrupt paths. The searched references show `GLINT_*` used for interrupt arming and vector-to-function mapping, `PF_FW_ATQLEN_*` used for AdminQ error handling, and `GLTSYN_*` used extensively by PTP.

## Risks
Because the file is machine generated, manual edits are high risk and likely to diverge from hardware specifications. Incorrect offsets or masks can cause silent hardware misconfiguration. Indexed macros need caller-side range discipline; only a few include explicit max-index macros. Hardware-generation differences are encoded in `E800_` and `E830_` variants, so callers must select the correct macro for `hw->mac_type`.

## Test signals
Build coverage catches missing macro names but not semantic offset errors. Functional signals include AdminQ health, interrupt delivery, queue enable/disable, SR-IOV vector mapping, PTP clock behavior, flow director configuration, statistics reads, and ethtool register dumps.
