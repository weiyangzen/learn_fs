# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/ethtool.c

## Purpose

This file implements the e1000e driver's ethtool interface. It exposes link settings, pause parameters, register dumps, EEPROM access, ring sizing, private flags, coalescing, Wake-on-LAN, LED identification, statistics, RSS hash fields, EEE, timestamp capabilities, and online/offline diagnostics to user space.

## Important APIs, Types, and Functions

The file installs `e1000_ethtool_ops` through `e1000e_set_ethtool_ops()`. Important operation handlers include `e1000_get_link_ksettings()`, `e1000_set_link_ksettings()`, `e1000_get_pauseparam()`, `e1000_set_pauseparam()`, `e1000_get_regs()`, `e1000_get_eeprom()`, `e1000_set_eeprom()`, `e1000_get_ringparam()`, `e1000_set_ringparam()`, `e1000_diag_test()`, `e1000_get_wol()`, `e1000_set_wol()`, `e1000_set_phys_id()`, `e1000_get_coalesce()`, `e1000_set_coalesce()`, `e1000_get_ethtool_stats()`, `e1000_get_rxfh_fields()`, `e1000e_get_eee()`, `e1000e_set_eee()`, `e1000e_get_ts_info()`, `e1000e_get_priv_flags()`, and `e1000e_set_priv_flags()`.

`struct e1000_stats` maps ethtool statistic names to either `struct rtnl_link_stats64` or `struct e1000_adapter` offsets. The private flags are `s0ix-enabled` and `disable-k1`.

Diagnostic helpers include register pattern tests, EEPROM checksum tests, interrupt forcing tests, descriptor-ring setup/free for loopback, PHY/MAC/fiber loopback setup and cleanup, loopback frame creation/verification, and link tests.

## Control Flow

Setters that alter hardware-visible state generally acquire the reset gate by setting `__E1000_RESETTING`, then reset or cycle the interface. Link setting changes validate SoL/IDER reset blocks, MDI/MDI-X restrictions, autonegotiation, speed, and duplex before calling `e1000e_down()`/`e1000e_up()` or `e1000e_reset()`. Pause changes either restore default autonegotiated flow control or force MAC flow control and watermarks.

EEPROM reads compute word ranges around byte offsets, allocate a temporary buffer, read via NVM ops, endian-convert, and copy the requested byte span. EEPROM writes validate magic and read-only flags, preserve partial leading/trailing words with read-modify-write, convert endianness, write through NVM ops, and update checksums when needed.

Ring resizing clamps and aligns descriptor counts, blocks concurrent reset, optionally allocates replacement rings while the interface is down, then swaps resources so MSI-X handlers that reference ring structures remain valid.

Offline diagnostics close the interface if running, run register, EEPROM, interrupt, loopback, and link tests with resets between stages, restore saved autoneg/speed state, and reopen the interface. Online diagnostics only run the link test. Loopback diagnostics allocate test rings, program Tx/Rx descriptors and MAC/PHY loopback mode, transmit recognizable frames, poll Rx buffers for matching markers, then clean up.

## State and Persistence Behavior

The file reads and mutates `struct e1000_adapter` fields including link settings, `fc_autoneg`, `msg_enable`, ring counts, WOL mask, interrupt mode, test interrupt cause, test rings, `itr`/`itr_setting`, `flags2`, `eee_advert`, and saved loopback scratch state. It reads/writes hardware registers, PHY registers, and NVM contents. EEPROM writes and WOL device wake settings can persist beyond the immediate ethtool call.

Diagnostic paths are intentionally disruptive in offline mode: they reset hardware, alter loopback bits, allocate DMA rings, request/free IRQs, and close/reopen the netdev. Cleanup restores loopback state, frees DMA mappings, and clears testing/reset bits.

## Dependencies and Integration Points

This file integrates Linux ethtool, netdev, PCI, DMA, IRQ, PM runtime, MII/MDIO, EEE, and timestamping APIs with e1000e internal helpers from `e1000.h`. It relies on operation vectors initialized by hardware-family files such as `82571.c`, and on constants from `defines.h`, `hw.h`, PHY headers, and register definitions.

## Risks and Edge Cases

Risk concentrates around user-triggered hardware mutation. EEPROM writes can persist bad configuration if validation or checksum handling fails. Offline tests intentionally disrupt traffic. Interrupt tests temporarily force legacy mode when MSI-X is active. Ring resizing must not free structures still referenced by interrupt handlers. Loopback setup has many MAC/PHY-specific paths and requires cleanup to avoid leaving loopback or forced-link state enabled. Setters must consistently clear `__E1000_RESETTING` on all exits.

Input validation is important for unsupported speed/duplex combinations, MDI settings without autonegotiation, unsupported WOL masks, read-only NVM, EEE advertisement limited to 100/1000 full duplex, unsupported S0ix or K1 private flags, and coalescing values outside supported ITR ranges.

## Test Signals

Direct test signals are `ethtool -i`, `-k/-S/-d/-e/-E`, `-g/-G`, `-c/-C`, `-a/-A`, `-s`, `-r`, `-p`, `-t online`, and `-t offline` on representative hardware. Strong automated checks include concurrent reset/ring-setting stress, EEPROM read/write failure injection, WOL suspend/resume, EEE get/set on supported PCH PHYs, timestamp capability reporting on 82574/82583, and loopback cleanup verification after test failure.
