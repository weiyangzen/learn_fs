# sources/distributed-fs/orangefs/src/client/sysint/mgmt-get-config.c
## sources/distributed-fs/orangefs/src/client/sysint/mgmt-get-config.c

**Purpose:** Implements `PVFS_mgmt_get_config()`, which fetches a filesystem configuration buffer from a server through the client state-machine framework.

**APIs and control flow:** The function allocates a `PVFS_SERVER_GET_CONFIG` SMCB, marks config buffers persistent, initializes message-array params and credentials, maps the target BMI address to a config-server string, finds the filesystem configuration, fills a transient mount entry, initializes the message pair, posts the state machine, waits via `PVFS_mgmt_wait`, copies the retrieved config buffer to caller storage, frees persistent config buffer, and releases the op ID.

**State and dependencies:** Depends on cached config, server config manager, message-pair encoding, credentials, sysint SM runtime, and config structures.

**Risks and tests:** It calls `PINT_put_server_config_struct(config)` before using `config` and `cur_fs`, which relies on manager reference semantics not invalidating the pointer. It does not check all nulls returned from config lookup/map before dereferencing. Tests should cover unknown fsid/address, small output buffers, wait/post errors, credential failure, and buffer termination.
