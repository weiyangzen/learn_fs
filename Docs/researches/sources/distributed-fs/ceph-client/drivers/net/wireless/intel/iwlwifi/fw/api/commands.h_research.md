# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/commands.h

Purpose: Provides the central firmware command namespace: command groups, legacy opcodes, system subcommands, and statistics subcommands used by iwlwifi host-command dispatch.

Important APIs and types: `enum iwl_mvm_command_groups` assigns group IDs such as legacy, system, MAC config, PHY ops, datapath, scan, location, BT coexistence, regulatory/NVM, debug, and statistics. `enum iwl_legacy_cmds` maps legacy opcodes for ALIVE, scan, station/key, TX, scheduler, MAC/PHY context, time events, LED, link quality, statistics, RX, BT, D3/WoWLAN, debug, and multicast filtering. `enum iwl_system_subcmd_ids` and `iwl_statistics_subcmd_ids` define grouped newer commands.

Control flow: No executable flow; all host command construction and notification dispatch depend on these numeric IDs.

State and persistence: Header owns no state. The numeric values are persistent firmware ABI and must remain stable for supported firmware images.

Dependencies and integration points: Cross-references structures from many API headers (`alive.h`, `binding.h`, `d3.h`, `datapath.h`, `debug.h`, `filter.h`, `led.h`, scan/rx/tx/etc.). Used by transport command submission, notification wait registration, debug tooling, DVM and MVM operation modes.

Risks: Opcode reuse and version-specific payload selection are easy to mismatch. Some legacy IDs document several payload versions. `LONG_GROUP` and `IWL_ALWAYS_LONG_GROUP` interaction in command headers must be preserved. Adding commands in the wrong group can break firmware routing.

Test signals: Compile all command users, validate command IDs against firmware TLV API versions, exercise notification dispatch for legacy and grouped commands, and run firmware init/runtime flows that touch ALIVE, TX, scan, statistics, debug, D3, and datapath commands.
