# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/debug.c

Purpose: Implements debugfs helpers and firmware memory coredump creation for debug-enabled brcmfmac builds.

Important APIs/types/functions: `brcmf_debug_create_memdump()` allocates optional event data plus RAM dump, calls bus memdump retrieval, and emits `dev_coredumpv()`. `brcmf_debugfs_get_devdir()` returns the wiphy debugfs directory. `brcmf_debugfs_add_entry()` creates device-managed seqfile entries.

Control flow: Firmware watchdog/crash paths call memdump creation. Core/feature/proto/bus code add debugfs entries after wiphy registration.

State and persistence behavior: Coredumps are retained by kernel devcoredump infrastructure. Debugfs files persist for device lifetime via devm cleanup.

Dependencies and integration points: Uses bus `get_ramsize`/`get_memdump`, debugfs, wiphy debugfs, and devcoredump.

Risks: Large RAM dumps can fail allocation. Failed bus memdump frees the buffer and emits no dump. Debugfs creation warns if wiphy debugfs is unavailable.

Test signals: Trigger firmware crash/PSM watchdog and verify devcoredump; verify debugfs entries exist and disappear on removal.
