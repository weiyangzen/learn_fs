<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/debug.c

Purpose: Implements optional debugfs controls for WCN36xx BMPS power-save switching, firmware dump commands, and firmware feature capability display.

Important APIs/types/functions: Under `CONFIG_WCN36XX_DEBUGFS`, defines debugfs file operations for `bmps_switcher`, `dump`, and `firmware_feat_caps`, and exports `wcn36xx_debugfs_init()` / `wcn36xx_debugfs_exit()`.

Control flow: Init creates a `wcn36xx` debugfs directory under the wiphy debugfs root and adds files. BMPS reads scan station vifs for `WCN36XX_BMPS`; writes parse the first user byte and enter/exit BMPS via keepalive/PMC helpers. Dump writes parse up to five integer arguments and send an SMD dump command. Firmware feature reads allocate a buffer, lock `hal_mutex`, enumerate supported feature bits, and copy names to userspace. Exit removes the debugfs tree.

State and persistence: Mutates firmware/driver power-save state through PMC calls and stores debugfs dentries in `wcn->dfs`. No durable persistence.

Dependencies and integration points: Depends on debugfs, usercopy, WCN36xx vif list, PMC, firmware feature helpers, SMD command path, and `wcn->hal_mutex`.

Risks and test signals: Risks include vif-list iteration without explicit locking context, silent ignore of invalid BMPS input, fixed feature buffer truncation, and debugfs creation failure. Test signals are debugfs file presence, BMPS enter/exit on station mode, dump command dispatch, and firmware capability listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/debug.c -->
