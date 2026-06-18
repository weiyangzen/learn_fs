# sources/distributed-fs/ceph-client/drivers/platform/x86/xo1-rfkill.c

Purpose: OLPC XO-1 platform rfkill driver that controls WLAN reset through the OLPC embedded controller.

Important APIs/types/functions: global `card_blocked` tracks the last successfully applied software block state. `rfkill_set_block()` sends `EC_WLAN_ENTER_RESET` or `EC_WLAN_LEAVE_RESET` via `olpc_ec_cmd()`. `xo1_rfkill_probe()` allocates/registers an `RFKILL_TYPE_WLAN` device, and `xo1_rfkill_remove()` unregisters/destroys it.

Control flow: platform probe creates the rfkill object with `rfkill_ops`. When userspace changes block state, `rfkill_set_block()` skips redundant commands, chooses the EC command for block/unblock, sends it, and updates `card_blocked` only on success. Remove tears down the rfkill object.

State and persistence: only `card_blocked` persists in memory across rfkill operations while the module is loaded. The EC controls actual WLAN reset state; there is no persistent storage.

Dependencies/integration: depends on platform-device registration under alias `platform:xo1-rfkill`, Linux rfkill core, and OLPC EC command support.

Risks: the initial `card_blocked` state is assumed false and not read back from EC, so software and hardware state can be out of sync after boot or failed commands. A single global state is adequate only for one device. EC command failures leave state unchanged and must be surfaced to rfkill callers.

Test signals: rfkill list should show a WLAN switch; blocking/unblocking should issue EC reset commands and affect the card; duplicate state writes should avoid EC traffic; EC failures should propagate; remove should unregister without dangling rfkill entries.
