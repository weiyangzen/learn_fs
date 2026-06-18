# sources/distributed-fs/ceph-client/drivers/net/phy/mscc/mscc_ptp.h

Purpose: defines the VSC85xx 1588/PTP register map, analyzer comparator fields, local time counter fields, FIFO formats, PTP command encodings, and software structures consumed by `mscc_ptp.c`.

Important APIs/types:
- BIU indirection macros (`MSCC_PHY_TS_BIU_ADDR_CNTL`, `BIU_ADDR_EXE`, `BIU_BLK_ID()`, `BIU_CSR_ADDR()`) define how the C file reads and writes 1588 CSR blocks through the base PHY.
- Processor registers describe interface control, analyzer mode, LTC load/save/adjust, predictor enable bits, latency registers, delay FIFO depth, timestamp FIFO control, rewriter controls, serial TOD behavior, and accuracy calibration status.
- Analyzer register groups define Ethernet, IP, MPLS, OAM/PTP, and PTP flow enable/match/mask/action registers. `COMP_MAX_FLOWS` is 8 for generic comparators; `PTP_COMP_MAX_FLOWS` is 6 for PTP flows.
- `enum ptp_cmd` maps hardware rewrite/save commands such as `PTP_WRITE_1588`, `PTP_WRITE_NS`, and the software sentinel `PTP_SAVE_IN_TS_FIFO`.
- `struct vsc85xx_ptphdr` is a packed PTP header view used to parse or update packet fields.
- `struct vsc85xx_ts_fifo` models one egress timestamp FIFO entry as nanoseconds, 48-bit seconds, and a 16-byte signature.
- `struct vsc85xx_ptp` stores per-PHY PHC/timestamper runtime state.

Control flow enabled by this header: `mscc_ptp.c` uses the macros to build comparator chains from Ethernet to PTP directly for L2 (`ETH_P_1588`) or through IPv4/UDP to PTP for L4 event traffic. Flow action macros encode whether ingress writes nanoseconds into packet reserved bytes, whether egress rewrites one-step timestamps, or whether egress saves a timestamp/signature into the FIFO. LTC macros encode PHC load/save and frequency/offset adjustment. FIFO macros let the interrupt handler detect empty/overflow/level conditions and reset the FIFO.

State and persistence: the header declares both software queue/clock state (`struct vsc85xx_ptp`) and packed wire/hardware views. Hardware state described here persists in the 1588 processor until reset or reconfiguration. FIFO entries are consumed destructively by reading the last FIFO word. The software `configured` bit gates RX/TX timestamp callbacks after hwtstamp configuration.

Dependencies and integration points: requires phylib/PHY declarations, PTP clock types, SKB queue types, and kernel bit macros supplied by included users. It is tightly coupled to `mscc_ptp.c`; `mscc.h` forward-declares `struct vsc85xx_ptp` usage in private driver state and exposes PTP entry points conditionally under `CONFIG_NETWORK_PHY_TIMESTAMPING`.

Risks and edge cases:
- Many macros use literal bit masks instead of `FIELD_PREP`, so invalid values can spill into adjacent fields if callers do not constrain inputs.
- The packed bitfield `u64 secs:48` in `struct vsc85xx_ts_fifo` is compiler-layout-sensitive; the C file fills it byte by byte, so ABI assumptions should be validated on target architectures.
- PTP header parsing structures only model the fields needed by this implementation; unsupported PTP transports or IPv6 are outside this header's flow model.
- Delay constants such as `PTP_INGR_DELAY_FIFO_DEPTH_MACSEC` and `STALL_EGR_LATENCY()` encode hardware timing assumptions that must match MACsec/PTP pipeline changes.

Test signals: build with `CONFIG_NETWORK_PHY_TIMESTAMPING`; run sparse/packed-structure checks; validate CSR addresses against datasheet; exercise L2 and L4 hwtstamp modes; verify egress FIFO entry byte layout against actual hardware FIFO dumps; test PHC adjustment fields over positive and negative offsets/frequency corrections.
