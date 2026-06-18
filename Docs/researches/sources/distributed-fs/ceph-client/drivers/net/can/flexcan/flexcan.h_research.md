# sources/distributed-fs/ceph-client/drivers/net/can/flexcan/flexcan.h

Purpose: this header shares FlexCAN private driver definitions between the core and ethtool files. It documents hardware feature flags, defines the per-SoC quirk bits, declares the device private state, and provides small helpers for RX mailbox/FIFO/RTR capability decisions.

Important APIs, types, and functions: `struct flexcan_devtype_data` carries the quirk bitmap selected by platform or OF match data. `struct flexcan_stop_mode` stores a syscon regmap and bit location for GPR stop mode. `struct flexcan_priv` embeds `struct can_priv` and `struct can_rx_offload`, then stores register pointers, mailbox pointers and dimensions, masks, clocks, transceiver resources, stop-mode firmware data, IRQ numbers, and endian read/write callbacks. Inline helpers are `flexcan_supports_rx_mailbox()`, `flexcan_supports_rx_mailbox_rtr()`, `flexcan_supports_rx_fifo()`, and `flexcan_active_rx_rtr()`. The header declares `flexcan_ethtool_ops`.

Control flow: the header itself has no runtime control flow, but its helpers are used by ethtool to decide whether a requested `rx-rtr` private flag means mailbox mode or FIFO mode. The core driver fills `struct flexcan_priv` during probe and open, then reads its quirk and mailbox fields throughout bit timing, RX offload, interrupt, PM, and TX paths.

State and persistence: the header defines the shape of all FlexCAN runtime state. The quirk bitmap is copied from static match data into each device and can be modified by ethtool before the interface is opened. Stop-mode state persists for the lifetime of the platform device and is consumed by suspend/resume.

Dependencies and integration points: it includes `linux/can/rx-offload.h` and assumes Linux CAN, clock, regulator, PHY, regmap, i.MX SCU, and MMIO types are visible through the C files that include it. The exported ethtool ops declaration is the link between `flexcan-core.c` and `flexcan-ethtool.c`.

Risks: quirk bits are a compact contract across files; adding or changing one requires auditing core startup, RX offload, PM, ethtool mode selection, and compatible data. `struct flexcan_priv` exposes direct register access callbacks and hardware mailbox pointers, so invalid `mb_count` or `mb_size` calculations in the core can corrupt MMIO accesses.

Test signals: compile coverage should catch missing type declarations and exported ops mismatches. Runtime signals are correct quirk-derived behavior per compatible, ethtool `rx-rtr` behavior, CAN FD capability gating, stop-mode wakeup, and mailbox/FIFO receive mode selection.
