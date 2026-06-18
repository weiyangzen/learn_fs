# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_devlink.h

Purpose: Declares the devlink-facing Prestera lifecycle, port registration, and trap reporting API used by the rest of the driver.

Important APIs/types/functions: Exports prototypes for switch devlink allocation/free/register/unregister, devlink port register/unregister, trap register/unregister, and `prestera_devlink_trap_report()`. Includes `prestera.h` for switch, port, device, and skb-adjacent type visibility.

Control flow: This header is consumed by switch setup/teardown in `prestera_main.c`, packet receive paths that report traps, and the devlink implementation itself. It does not define state or inline behavior.

State and persistence: No direct state. It exposes functions that operate on `struct prestera_switch`, `struct prestera_device`, `struct prestera_port`, and `struct sk_buff` owned elsewhere.

Dependencies/integration: Couples `prestera_main.c` to the devlink module while hiding trap table internals. Also provides the public hook used by RX/TX code to translate firmware CPU code metadata into devlink trap notifications.

Risks: Prototype drift against `prestera_devlink.c` would break builds. Because it includes the broad `prestera.h`, changes in central structures can ripple into all include users.

Test signals: Compile coverage is the primary signal. Runtime signals are successful switch probe, devlink port registration, trap registration, and trapped packet reports through call sites declared here.
