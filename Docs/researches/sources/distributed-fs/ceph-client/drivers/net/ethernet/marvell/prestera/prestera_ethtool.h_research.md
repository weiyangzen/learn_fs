# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_ethtool.h

Purpose: Declares the Prestera ethtool operations table for netdev setup.

Important APIs/types/functions: Provides `extern const struct ethtool_ops prestera_ethtool_ops;` and forward declarations for Prestera port/event types.

Control flow: `prestera_main.c` assigns this table to each created netdev. The actual callbacks live in `prestera_ethtool.c`.

State and persistence: No direct state. It exposes an immutable ops table.

Dependencies/integration: Includes `<linux/ethtool.h>`. Used by port creation to connect ethtool user requests to firmware-backed port operations.

Risks: Header is intentionally small; drift between the extern declaration and implementation would be caught at build/link time.

Test signals: Compile/link success and `netdev->ethtool_ops` behavior on registered Prestera ports.
