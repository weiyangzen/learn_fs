# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe.h

Purpose: central private header for the Mucse rnpgbe 1GbE PCIe driver. It defines board IDs, core hardware/mailbox state, driver-private netdev state, public internal function prototypes, PCI device IDs, and a simple MMIO write helper.

Important APIs/types: `enum rnpgbe_boards` distinguishes N500 and N210 board families. `struct mucse_mbx_info` stores mailbox timing, counters, lock, shared-memory base, and control/mask offsets. `struct mucse_hw` stores MMIO base, PCI device, mailbox, port, and PF/VF number. `struct mucse` is netdev private state with `netdev`, `pdev`, `hw`, and `stats`. Prototypes connect `rnpgbe_main.c`, `rnpgbe_chip.c`, and firmware mailbox code.

Control flow: no executable flow, but the structs shape probe-time initialization and mailbox request paths.

State and persistence: runtime state is in `struct mucse` allocated by `alloc_etherdev_mq`. Mailbox counters `fw_req` and `fw_ack` mirror firmware registers and are used to detect new messages/acks.

Dependencies and integration: includes Linux types and mutex support. Used by all rnpgbe translation units.

Risks: `mucse_hw_wr32` performs unchecked MMIO offset writes relative to BAR mapping; board-specific offsets must be initialized first. `struct mucse_stats` currently only tracks dropped TX, matching the minimal transmit implementation.

Test signals: compile coverage and probe on each PCI ID; inspect netdev private state after init; verify valid MAC path and fallback random MAC path.
