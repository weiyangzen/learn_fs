# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-rgmii.c

## Purpose
RGMII/GMII open and link polling support, including a 10Mbps preamble-error workaround.

## Important APIs, Types, And Functions
Exports `cvm_oct_rgmii_open()`. Internal helpers are `cvm_oct_set_hw_preamble()`, `cvm_oct_check_preamble_errors()`, and `cvm_oct_rgmii_poll()`.

## Control Flow
Open calls common PHY/MAC setup with `cvm_oct_rgmii_poll()`. If phylib is used on true RGMII or GMII port 0, it installs periodic preamble checking. The checker takes a global register lock, watches speed changes and GMX preamble error bits, disables hardware preamble checking/FCS stripping for broken 10Mbps links, or re-enables hardware handling when speed changes. Link polling reads CVMX link info, applies it to hardware, updates carrier, and logs changes.

## State And Persistence
Uses global `global_register_lock` plus per-port `last_speed`, `link_info`, `last_link`, and `poll` fields. State is volatile.

## Dependencies And Integration Points
Depends on common open/stop/link helpers, phylib, netdev carrier, and CVMX GMX/IPD CSR access.

## Risks
Global CSR changes affect more than one port, so locking is critical. The software preamble workaround is hardware- and speed-specific. Incorrect `phy_mode` or DT delay settings in `ethernet.c` can affect this path.

## Test Signals
RGMII and GMII open, PHY and no-PHY operation, 10Mbps preamble errors, speed changes re-enabling hardware checks, carrier transitions, and concurrent polling on multiple ports.
