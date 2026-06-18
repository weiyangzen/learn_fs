<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc911x.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc911x.h

## Purpose
`smsc911x.h` is the local register and bitfield contract for the LAN911x/LAN921x platform driver. It defines chip IDs, FIFO thresholds, EEPROM size, NAPI weight, debug macros, optional PHY loopback workaround, direct register offsets, indirect MAC CSR offsets, PHY interrupt bits, and architecture hook points.

## Important APIs, Types, and Functions
There are no exported functions or structures in this header. Its API is the macro set consumed by `smsc911x.c`: chip ID constants such as `LAN9115`, `LAN9218`, `LAN9221`, `LAN9250`, `LAN89218`; FIFO and status registers such as `RX_DATA_FIFO`, `TX_DATA_FIFO`, `RX_STATUS_FIFO`, `TX_STATUS_FIFO`, `ID_REV`, `INT_CFG`, `INT_STS`, `INT_EN`, `FIFO_INT`, `RX_CFG`, `TX_CFG`, `HW_CFG`, `PMT_CTRL`, `GPIO_CFG`, `MAC_CSR_CMD`, `E2P_CMD`; and indirect MAC registers such as `MAC_CR`, `ADDRH`, `ADDRL`, `HASHH`, `HASHL`, `MII_ACC`, `MII_DATA`, `FLOW`, `VLAN1`, `WUCSR`.

## Control Flow
The header shapes driver control flow by naming the bits that gate reset, FIFO movement, interrupt enable/ack, MAC CSR read/write, MII transactions, EEPROM commands, wake events, GPIO LEDs, and PHY status. `SMSC_WARN` and `SMSC_TRACE` compile to `netif_*` logging only when `USE_DEBUG` is raised; otherwise they compile to `no_printk`. `SMSC_ASSERT_MAC_LOCK` integrates lockdep for indirect MAC accesses when spinlock debugging is enabled. `SMSC_INITIALIZE()` and `smsc_get_mac()` are default hooks that can be overridden by `CONFIG_SMSC911X_ARCH_HOOKS`.

## State and Persistence Behavior
The defined registers represent volatile device state: FIFO occupancy, interrupt latches, MAC enable bits, GPIO/LED configuration, PHY power and wake bits, and MDIO transaction state. EEPROM command/data macros expose persistent storage operations when called by the ethtool code. The header itself stores no state.

## Dependencies and Integration Points
It includes `linux/smscphy.h` and optionally `asm/smsc911x.h`. It is tightly coupled to `smsc911x.c` and to firmware bindings that supply compatible devices, bus width, shift, IRQ polarity/type, PHY mode, supplies, reset GPIO, and MAC-address properties.

## Risks
Changing constants can corrupt MMIO or EEPROM operations. Some names represent device-specific behavior only present on selected chips, such as external PHY control on 9115/9117 and 32/16-bit mode on 9116/9118. `USE_PHY_WORK_AROUND` is enabled at header level, so build-time changes affect probe behavior. Debug macro changes can hide or expose logging in timing-sensitive paths.

## Test Signals
Build and boot-test every supported ID family, verify `BYTE_TEST`/`WORD_SWAP`, reset through `HW_CFG` and LAN9250 `RESET_CTL`, MDIO read/write through `MII_ACC`, interrupt enable/status bits, EEPROM read/write commands, WOL/PMT transitions, and multicast hash programming through `HASHH/HASHL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc911x.h -->
