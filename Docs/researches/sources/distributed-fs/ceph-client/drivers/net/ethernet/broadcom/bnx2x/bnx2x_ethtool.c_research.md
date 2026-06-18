# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_ethtool.c

## Purpose
Implements the `bnx2x` ethtool interface for PFs and VFs. It exposes link settings, register dumps, firmware/driver info, wake-on-LAN, message levels, link reset, EEPROM/NVRAM and module EEPROM access, coalescing, ring sizes, pause settings, EEE, self-tests, statistics, physical identification LEDs, RSS hash configuration, RSS indirection, channel count, timestamp capabilities, and ethtool operation table selection.

## Important APIs, Types, and Functions
The top-level integration point is `bnx2x_set_ethtool_ops`, which installs either `bnx2x_ethtool_ops` for PFs or `bnx2x_vf_ethtool_ops` for VFs. Link operations include `bnx2x_get_link_ksettings`, `bnx2x_set_link_ksettings`, and the VF-specific `bnx2x_get_vf_link_ksettings`. Register dump operations include `bnx2x_get_regs_len`, `bnx2x_get_regs`, `bnx2x_set_dump`, `bnx2x_get_dump_flag`, and `bnx2x_get_dump_data`.

NVRAM/EEPROM helpers include `bnx2x_acquire_nvram_lock`, `bnx2x_release_nvram_lock`, `bnx2x_enable_nvram_access`, `bnx2x_disable_nvram_access`, `bnx2x_nvram_read_dword`, exported `bnx2x_nvram_read`, `bnx2x_nvram_read32`, `bnx2x_nvram_write_dword`, `bnx2x_nvram_write1`, `bnx2x_nvram_write`, `bnx2x_get_eeprom`, `bnx2x_set_eeprom`, `bnx2x_get_module_eeprom`, and `bnx2x_get_module_info`.

Self-test support is built around `bnx2x_test_registers`, `bnx2x_test_memory`, `bnx2x_run_loopback`, `bnx2x_test_loopback`, `bnx2x_test_ext_loopback`, `bnx2x_test_nvram`, `bnx2x_test_intr`, and `bnx2x_self_test`. Statistics and strings are driven by `bnx2x_q_stats_arr`, `bnx2x_stats_arr`, `bnx2x_tests_str_arr`, `bnx2x_private_arr`, `bnx2x_get_sset_count`, `bnx2x_get_strings`, and `bnx2x_get_ethtool_stats`.

RSS/channel operations include `bnx2x_get_rxfh_fields`, `bnx2x_set_rxfh_fields`, `bnx2x_get_rxfh_indir_size`, `bnx2x_get_rxfh`, `bnx2x_set_rxfh`, `bnx2x_get_channels`, `bnx2x_change_num_queues`, and `bnx2x_set_channels`.

## Control Flow
PF ethtool ops expose the full feature set; VF ops expose a reduced set that omits hardware-owned features such as register dumps, EEPROM writes, self-tests, WOL, pause, EEE, and module EEPROM. Link setting reads combine board-supported modes, active PHY media type, current link state, multi-function speed policy, autonegotiation state, and link-partner status. Link setting writes validate multi-function restrictions, requested port type, autoneg advertisements, forced speed/duplex support, and then update `link_params`; if the device is running, they stop stats, reset link, and call `bnx2x_link_set`.

Register dumps compute lengths from `bnx2x_dump.h`, write a `dump_header`, disable parity attentions, iterate idle/regular/windowed/paged register tables, then clear and re-enable parity. Preset dump operations use `ethtool_dump.flag` as a preset index.

NVRAM reads/writes serialize through a hardware NVRAM lock, request MCP NVM software arbitration, enable access bits, issue command registers with FIRST/LAST page flags, poll for DONE, and release access. Writes across 4 KiB page boundaries release the lock briefly so MFW can make progress. Module EEPROM operations use PHY I2C reads under the PHY lock and split A0/A2 SFP address spaces.

Self-test first runs online NVRAM CRC checks, then, if the device is up and offline tests are requested on non-MF PFs, unloads/reloads the NIC in diagnostic mode, runs register/memory/internal loopback tests, optionally runs external loopback, restores the normal load, then runs interrupt and link tests. Loopback sends a crafted packet through the first queue and validates TX completion, RX completion, length, and payload.

## State and Persistence Behavior
The file reads and mutates many fields in `struct bnx2x`: link parameters, advertised modes, flow-control requests, `wol`, `msg_enable`, `dump_preset_idx`, NVRAM flash size, coalescing ticks, ring sizes, EEE mode, RSS configuration, queue counts, stats blocks, and PTP clock state. It also changes persistent hardware/firmware state through NVRAM writes, PHY firmware-upgrade magic commands, LED control, link reset/init, RSS reconfiguration, interrupt mode changes, and NIC unload/load cycles.

## Dependencies and Integration Points
Depends on Linux ethtool, netdevice, PCI power-management state, CRC32, DMA mapping, SKB allocation, PHY/module EEPROM helpers, `bnx2x.h`, `bnx2x_cmn.h`, `bnx2x_dump.h`, `bnx2x_init.h`, firmware/shared-memory macros, register access, link management, queue state ramrods, RSS helpers, statistics events, and PTP APIs. Main-driver probe calls `bnx2x_set_ethtool_ops`; other driver files call exported `bnx2x_nvram_read` for firmware/NVM consumers.

## Risks
NVRAM access is high risk because lock ordering must protect PFs on the same port and MFW arbitration, while endian behavior is intentionally historical: reads convert to big-endian byte streams but writeback preserves old tool expectations. Link setting paths have many board, media, multi-phy, and multi-function restrictions; missing a validation branch can advertise or force unsupported modes. Register dump tables can produce false parity/GRC noise if parity is not disabled and restored correctly. Self-tests unload/reload the NIC and manipulate queues, DMA mappings, PHY locks, and loopback state, so failures can leave link or queue state disrupted if cleanup changes regress. RSS and channel setters reject VF/SRIOV cases and unsupported hash parameters; changing queue counts requires interrupt-mode teardown/rebuild.

## Test Signals
Useful coverage includes `ethtool -i`, `-k/-S/-g/-G/-c/-C/-a/-A`, `ethtool -d`, preset dump ioctls, WOL get/set, speed/autoneg/port switching on supported boards, SFP module info/eeprom reads, EEPROM read/write with alignment and one-byte writes, EEE get/set, offline and online self-tests, external loopback where cabled, VF ethtool behavior, RSS hash field changes, indirection table round-trips, channel count changes with and without VFs enabled, PTP timestamp info, and suspend/down-state NVM access rejection.
