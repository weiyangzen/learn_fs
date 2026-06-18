# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_debugfs.c

## Purpose

`i40e_debugfs.c` provides the i40e debugfs interface when `CONFIG_DEBUG_FS` is enabled. It creates per-PF debugfs files that accept textual commands for dumping internal state, manipulating test switch objects, reading/writing registers, sending AdminQ commands, controlling LLDP, reading NVM, and invoking selected netdev operations.

## Important APIs, Types, And Functions

- `i40e_dbg_init()` and `i40e_dbg_exit()` create/remove the driver root debugfs directory.
- `i40e_dbg_pf_init()` and `i40e_dbg_pf_exit()` create/remove per-PF `command` and `netdev_ops` files.
- `i40e_dbg_command_write()` is the main command parser.
- `i40e_dbg_netdev_ops_write()` parses debug-triggered `change_mtu`, `set_rx_mode`, and `napi` commands.
- Dump helpers include `i40e_dbg_dump_vsi_seid()`, `i40e_dbg_dump_aq_desc()`, `i40e_dbg_dump_desc()`, `i40e_dbg_dump_veb_seid()`, `i40e_dbg_dump_vf()`, and stats dump helpers.
- `enum ring_type` selects Rx, Tx, or XDP descriptor rings for descriptor dumps.

## Control Flow

Driver init creates the debugfs root, each PF creates a directory named by `pci_name()`, and two write-only style files are installed with mode `0600`. Write handlers reject partial writes, copy a single user command, trim a newline, and dispatch by prefix.

The `command` parser supports state dump commands (`dump switch`, `dump vsi`, `dump veb`, `dump vf`, `dump desc`, `dump port`, `dump reset stats`, `dump debug fwdata`), topology/test changes (`add/del vsi`, `add/del relay`, `add/del pvid`), resets (`pfr`, `corer`, `globr`), register `read`/`write`, stats clearing, raw direct and indirect AdminQ command submission, Flow Director count dump, LLDP start/stop/MIB/event operations, and NVM reads. The `netdev_ops` parser calls selected netdev operations after VSI lookup and RTNL acquisition where needed.

## State And Persistence

The file owns global `i40e_dbg_root` and per-PF `pf->i40e_dbg_pf` dentries. Most commands inspect or mutate live PF/VSI/VEB/VF/hardware state only. Persistent or semi-persistent effects can occur through LLDP firmware start/stop, control-packet filters, DCBX capability changes, AdminQ commands, register writes, resets, and topology changes. Output goes to kernel logs via `dev_info()` and hex dumps.

## Dependencies And Integration Points

The file depends on debugfs, filesystem write callbacks, bridge definitions, i40e core PF/VSI/VEB/VF helpers, SR-IOV support, AdminQ helpers, LLDP AQ commands, NVM resource locking, XDP ring state, and netdev operations. It is compiled only under `CONFIG_DEBUG_FS`.

## Risks

- The command interface is powerful: raw register writes, raw AdminQ commands, resets, LLDP control, and topology changes can disrupt a live system.
- Prefix parsing with `strncmp()` and fixed offsets is brittle.
- Many dumps walk live driver structures; some use RCU or ring copies, but broader PF/VSI state can still race with teardown or reset.
- `i40e_dbg_dump_desc()` checks `vsi->tx_rings` even for Rx/XDP descriptor dumps.
- Debug output can be very large, especially descriptor rings, NVM dumps, and firmware debug data.

## Test Signals

Manual debugfs smoke tests should cover each command family, invalid argument handling, descriptor dumps for Rx/Tx/XDP, no-VF and invalid-VF paths, LLDP start/stop/get/event flows, register bounds checks, NVM read lock/unlock behavior, reset command scheduling, and netdev op RTNL contention. Kernel log volume should be monitored during large dumps.
