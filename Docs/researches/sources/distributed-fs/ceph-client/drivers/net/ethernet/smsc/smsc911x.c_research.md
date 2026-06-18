<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc911x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc911x.c

## Purpose
`smsc911x.c` is the platform driver for SMSC LAN911x/LAN921x/LAN922x/LAN9250 Ethernet controllers. It implements MMIO register and FIFO access, MDIO/phylib integration, netdev open/stop/xmit, NAPI receive, interrupt handling, multicast filtering, ethtool register/EEPROM access, power management, and device-tree/ACPI/platform-data configuration.

## Important APIs, Types, and Functions
The main private state is `struct smsc911x_data`, containing MMIO base, chip ID/generation, copied `smsc911x_platform_config`, MAC and device spinlocks, MDIO bus, PHY state, NAPI, multicast workaround state, register ops, regulators, reset GPIO, and clock. `struct smsc911x_ops` abstracts normal versus shifted register maps. Core routines include `smsc911x_reg_read/write`, FIFO helpers, `smsc911x_mac_read/write`, `smsc911x_mii_read/write`, `smsc911x_soft_reset`, `smsc911x_open`, `smsc911x_stop`, `smsc911x_hard_start_xmit`, `smsc911x_poll`, `smsc911x_irqhandler`, `smsc911x_drv_probe/remove`, and suspend/resume callbacks.

## Control Flow
Probe acquires memory and IRQ resources, maps registers, enables regulators/clock, parses firmware or platform data, selects shifted or standard ops, initializes chip identity/byte order, resets PHY/MAC, creates an MDIO bus, registers NAPI/netdev, and resolves the MAC address from firmware, platform data, EEPROM, saved hardware state, or random fallback. Open runtime-resumes the parent, connects to the PHY if needed, soft-resets hardware, configures FIFOs/GPIO/IRQ polarity, self-tests the interrupt path with a software interrupt, starts the PHY, enables NAPI, enables RX/TX interrupts, enables MAC RX/TX, and starts the queue. TX writes two command words and skb data into the TX FIFO, updates/free statuses, and stops the queue when FIFO space is low. RX IRQ disables RX interrupt and schedules NAPI; `smsc911x_poll` drains RX statuses, discards bad packets, reads FIFO payload into skbs, and reenables RX interrupts when complete.

## State and Persistence Behavior
Runtime state includes hardware FIFOs, interrupt masks/status, MAC CSR state, PHY registers, NAPI state, netdev counters, cached duplex/carrier, multicast hash data, and regulator/clock runtime PM state. EEPROM is persistent and exposed through ethtool byte reads/writes after explicit enable/disable write commands. MAC address persistence is conditional: `smsc,save-mac-address` preserves a bootloader-programmed address across reset; otherwise EEPROM/config/random sources are used.

## Dependencies and Integration Points
The driver integrates Linux platform bus, OF/ACPI property APIs, regulator and clock frameworks, GPIO descriptor reset, phylib/MDIO, NAPI/netdev, ethtool, runtime PM, and optional architecture hooks from `smsc911x.h`. Device-tree properties include `reg-io-width`, `reg-shift`, `phy-mode`, `smsc,irq-active-high`, `smsc,irq-push-pull`, PHY forcing flags, save-MAC flag, supplies, clock, and reset GPIO.

## Risks
High-risk areas are access width/shift mismatch, byte/word swapping, ordering around MAC CSR busy polling, early-generation multicast update restrictions, PHY energy-detect reset quirks, IRQ self-test failures, EEPROM timeout handling, and cleanup ordering across probe/open failures. `pm_runtime_get_sync()` return values are not always checked. The optional PHY loopback workaround can fail probe on marginal PHY paths.

## Test Signals
Test with 16-bit and 32-bit MMIO, shifted and non-shifted register maps, internal/external PHY selection, active-high/open-drain and push-pull IRQ modes, VLAN-sized frames, multicast/promiscuous modes on old and new generations, ethtool register/EEPROM reads and guarded writes, suspend/resume with wake settings, runtime PM cycling, and fault injection for regulator/clock/IRQ/MDIO allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smsc911x.c -->
