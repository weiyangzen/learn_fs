## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_drvinfo.h

Purpose: declaration header for driver information initialization.

Important APIs/types: forward-declares `struct net_device` and declares `int aq_drvinfo_init(struct net_device *ndev);`.

Control flow: none.

State and persistence: none.

Dependencies/integration: included by Atlantic initialization code to register optional hwmon support without exposing hwmon internals.

Risks: low; signature must match both `CONFIG_HWMON` and stub implementations.

Test signals: compile with hwmon enabled/disabled and call-site link checks.
