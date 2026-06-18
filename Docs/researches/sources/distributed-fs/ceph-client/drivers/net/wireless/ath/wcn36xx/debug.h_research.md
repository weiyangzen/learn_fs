<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/debug.h

Purpose: Declares WCN36xx debugfs data structures and init/exit hooks, with no-op stubs when debugfs support is disabled.

Important APIs/types/functions: Defines `WCN36xx_MAX_DUMP_ARGS`, `struct wcn36xx_dfs_file`, `struct wcn36xx_dfs_entry`, `wcn36xx_debugfs_init()`, and `wcn36xx_debugfs_exit()`.

Control flow: With `CONFIG_WCN36XX_DEBUGFS`, callers link to real implementations in `debug.c`; otherwise inline no-op functions preserve call sites.

State and persistence: Describes debugfs dentry state stored under `struct wcn36xx`. No standalone state.

Dependencies and integration points: Used by WCN36xx main driver lifecycle; depends on debugfs types when enabled.

Risks and test signals: Risks are structure drift with `debug.c` or call sites assuming debugfs files exist when stubs are compiled. Test signals are builds with debugfs enabled/disabled and clean init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/debug.h -->
