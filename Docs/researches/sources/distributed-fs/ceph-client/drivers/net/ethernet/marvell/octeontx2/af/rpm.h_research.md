# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rpm.h

## Purpose
`rpm.h` defines RPM/RPM2 device IDs, register offsets, bit masks, constants, and function prototypes for the CN10K RPM MAC implementation. It is the register contract used by `rpm.c`, CN10K channel programming in `rvu_cn10k.c`, and generic CGX/RPM integration code.

## Important APIs, Types, and Functions
- Device IDs include `PCI_DEVID_CN10K_RPM`, `PCI_SUBSYS_DEVID_CNF10KB_RPM`, and `PCI_DEVID_CN10KB_RPM`.
- Register macros describe common RPM CSRs such as `RPMX_CMRX_CFG`, `RPMX_CMR_GLOBAL_CFG`, `RPMX_CMRX_LINK_CFG`, `RPMX_MTI_MAC100X_COMMAND_CONFIG`, PCS loopback, statistics, FEC, pause, PFC, and timestamp mode registers.
- RPM2-specific macros describe alternative CSR offsets such as `RPM2_CMRX_SW_INT`, `RPM2_CMR_CHAN_MSK_OR`, `RPM2_CMR_RX_OVR_BP`, `RPM2_CMRX_PRT_CBFC_CTL`, `RPM2_CMRX_RX_LMACS`, and `RPM2_USX_PCSX_CONTROL1`.
- Bit masks include Rx/Tx enable, PTP prepend and one-step support, pause ignore/disable/forwarding bits, PFC class mask, FEC capture/clear bits, channel base/range fields, and X2P reset.
- Prototypes expose all RPM callback implementations used by the `mac_ops` tables, including LMAC count/type/FIFO queries, loopback, pause/PFC, stats, PTP, reset, and Rx/Tx control.

## Control Flow
The header has no runtime control flow. It shapes how `rpm.c` performs register read-modify-write sequences and how other files call RPM helpers. `rvu_cn10k.c` also uses `RPMX_CMRX_LINK_CFG` and its base/range masks when programming RPM channel windows.

## State and Persistence Behavior
The file defines hardware register layout rather than owning state. Values written through these macros persist in RPM/RPM2 CSRs until reset or later reconfiguration. The prototypes operate on opaque `void *rpmd`/`void *cgxd` handles that point to CGX/RPM private runtime state managed elsewhere.

## Dependencies and Integration Points
`rpm.h` includes Linux bit helpers and depends on types declared by included users, notably `struct cgx_fec_stats_rsp`. It is included by the RPM implementation and can be reached indirectly through CGX/RVU code. It forms the bridge between generic MAC operations and generation-specific RPM register offsets.

## Risks and Edge Cases
- Some macros are duplicated, such as pause and statistic register definitions; future edits must avoid diverging duplicate values.
- RPM and RPM2 offsets differ for several features; using RPM macros on RPM2 paths can write the wrong registers.
- Function prototypes use `void *` handles, so type safety is delegated to callers.
- Bitfield masks such as `RPM_PFC_CLASS_MASK` encode packed register layout; any hardware revision change needs coordinated updates in both header and implementation.

## Test Signals
- Compile-test all consumers after changing register macros or prototypes.
- Static analysis should check duplicate macro definitions for value consistency.
- Hardware register tests should verify RPM and RPM2 offsets used by `rpm.c` and `rvu_cn10k.c`.
- ABI-style tests should confirm `mac_ops` callback signatures stay aligned with prototypes in this header.
