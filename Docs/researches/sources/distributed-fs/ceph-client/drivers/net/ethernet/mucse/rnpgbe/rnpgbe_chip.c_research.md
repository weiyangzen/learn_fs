# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_chip.c

Purpose: board-level hardware helper layer for rnpgbe. It initializes board-specific mailbox bases, resets hardware through firmware, sends power notifications, and retrieves the permanent MAC address.

Important functions: `rnpgbe_get_permanent_mac` calls `mucse_mbx_get_macaddr` and validates the address. `rnpgbe_reset_hw` disables `RNPGBE_DMA_AXI_EN` before asking firmware to reset hardware. `rnpgbe_send_notify` dispatches notification modes, currently only `mucse_fw_powerup`. `rnpgbe_init_hw` chooses N500/N210 bases and initializes PF mailbox parameters.

Control flow: probe calls `rnpgbe_init_hw`, then power-up notify, firmware sync, reset, and MAC retrieval. Board init sets `hw->port = 0`, common mailbox control/mask offsets, then family-specific control/shared-memory bases.

State and persistence: mutates `struct mucse_hw` and `struct mucse_mbx_info` only. Hardware reset and power notifications affect device/firmware state but are not persisted by the driver.

Dependencies and integration: depends on `rnpgbe_hw.h` offsets, raw mailbox transport from `rnpgbe_mbx.c`, firmware commands from `rnpgbe_mbx_fw.c`, PCI device logging, and Ethernet address validation.

Risks: all board types currently force `hw->port = 0`; multi-port devices may need a reliable port derivation. Reset disables DMA before firmware reset; failures after this point can leave degraded hardware state. Unsupported board type returns `-EINVAL`.

Test signals: probe each supported device ID, firmware reset success/failure, invalid MAC fallback behavior, power-up/power-down notification logs, and mailbox base validation for N500 vs N210.
