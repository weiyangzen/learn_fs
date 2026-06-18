# sources/distributed-fs/ceph-client/drivers/net/can/rockchip/rockchip_canfd.h

Purpose: this header is the shared contract for all Rockchip CAN FD driver objects. It defines the register map, bitfields, hardware errata flags, core private structures, inline MMIO helpers, TX ring helpers, and cross-file function prototypes.

Important definitions: register macros cover classic/FD mode control, command, state, interrupt, bit timing, error-code, error counters, acceptance filters, TX/RX frame registers, timestamp registers, TX event/RX FIFO controls, and FIFO data windows. Constants define `DEVICE_NAME`, NAPI weight, two-entry TX FIFO depth, queue thresholds, timestamp worker limit, and a minimum clock warning for erratum 5. Quirk macros describe RK3568 errata and a `RKCANFD_QUIRK_CANFD_BROKEN` flag that disables exposed CAN FD capability.

Important types and APIs: `enum rkcanfd_model` distinguishes RK3568 v2/v3. `struct rkcanfd_devtype_data` stores model and quirk bits. `struct rkcanfd_fifo_header` mirrors FIFO header reads. `struct rkcanfd_stats` contains sequence-protected 64-bit erratum counters. `struct rkcanfd_priv` embeds `can_priv`, `can_rx_offload`, netdev, MMIO base, TX cursors, default mode/mask registers, devtype data, timecounter/cyclecounter, delayed timestamp work, corrected bus-error counters, stats, reset, and bulk clocks. Inline helpers wrap `readl`/`writel`/`readsl` and derive TX head/tail/pending/free.

Control flow and integration: the header has no runtime flow but defines how files call each other: core calls ethtool init and RX handling, TX exposes start_xmit and completion helpers, timestamp exposes skb timestamp and lifecycle helpers. Register macros are consumed throughout the split module.

State and persistence: state layout in `rkcanfd_priv` is the authoritative in-memory driver state. No data is persistent across unload. The header documents hardware errata in comments, including reproduction commands that are useful as validation signals.

Risks and test signals: register definitions are hardware ABI; mistakes silently corrupt MMIO access. Notable risk signal: `RKCANFD_REG_FD_RXDATA5` and `RKCANFD_REG_FD_RXDATA6` both define `0x320`, though RX data is read through the FIFO window rather than these macros in current code. Tests should include compile coverage for all split objects, sparse/endianness checks, RX/TX register encoding audits, and validation of quirk flags against OF match data.
