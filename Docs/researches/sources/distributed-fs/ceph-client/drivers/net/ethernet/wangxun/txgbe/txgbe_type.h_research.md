# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/txgbe/txgbe_type.h

Purpose: central TXGBE PF type and constant definition header. It records PCI IDs, subsystem/media IDs, register offsets, bit masks, Flow Director formats, SFP firmware-command payloads, software-node bookkeeping, IRQ metadata, and the main `struct txgbe` private state.

Important definitions: device IDs cover SP1000/WX1820 and AML variants. Register definitions include reset/status, port status, tunnel ports, XPCS IDA registers, I2C base, Flow Director tables and commands, Amber Lite MAC speed bits, EEPROM locations, queue limits, interrupt masks, and SFP/FEC capability values. `union txgbe_atr_input`, `union txgbe_atr_hash_dword`, `enum txgbe_atr_flow_type`, and `struct txgbe_fdir_filter` define software Flow Director inputs. Firmware HIC structures describe module-info, link-set/get, and I2C-read command payloads.

State and integration: `struct txgbe_nodes` stores software-node names, property arrays, references, and node groups used by `txgbe_phy.c`. `struct txgbe_irq` stores misc IRQ chip/domain data. `struct txgbe` points back to shared `struct wx`, owns PHY/SFP/I2C/clock/GPIO resources, tracks link and GPIO IRQs, stores Flow Director filters and masks, and caches link-mode masks.

Dependencies: includes Linux property/IRQ/PHY APIs and shared `libwx` types. It exports `txgbe_driver_name` and core lifecycle helpers such as `txgbe_down()`, `txgbe_up()`, `txgbe_setup_tc()`, and `txgbe_do_reset()`.

Risks and tests: the highest risk is silent mismatch between bit definitions and hardware/firmware contracts, especially FDIR, EEPROM, SFP/FEC, and MAC speed masks. Compile coverage, ethtool ntuple tests, SFP module probing, firmware mailbox commands, SR-IOV, and register-dump validation are key test signals.
