# sources/distributed-fs/lizardfs/src/tools/master_functions.cc

Purpose: Implements common master connection discovery, registration, and close helpers for tool commands.

Important APIs/types/functions: `open_master_conn`; `close_master_conn`; `force_master_conn_close`; static `master_register`; static `master_connect`; static `read_master_info`; thread-local `gCurrentMaster`; `master_info_t`.

Control flow: `open_master_conn` resolves a path, optionally rejects read-only filesystems, stats the object for inode/mode, closes any previous cached master socket, then walks upward looking for the special `.masterinfo` file. After reading ip/port/cuid/version, it connects with exponential-ish retry timeouts, registers as `REGISTER_TOOLS`, maps mount root inode to `SPECIAL_INODE_ROOT`, caches the socket, and returns it.

State and persistence: Maintains a thread-local current master socket. Reads `.masterinfo` special files from the mounted filesystem but does not write persistent state.

Dependencies and integration: Uses common serialization, socket helpers, special inode constants, and low-level legacy registration packets. All tools depend on this to locate and authenticate to the active master.

Risks and test signals: The global cached socket means multiple opens in one command must be reasoned about carefully. Path walking mutates a fixed-size `PATH_MAX` buffer. Registration is legacy-packed manually. No direct tests in this subset.
