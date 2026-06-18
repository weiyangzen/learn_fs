## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_main.h

Purpose: main Atlantic netdev interface declarations.

Important APIs/types: includes common/NIC headers, declares static key `aq_xdp_locking_key`, and exposes work scheduling, netdev allocation, open, and close functions.

Control flow: none.

State and persistence: declaration of `aq_xdp_locking_key` represents global runtime branch state controlled by XDP attach/detach in `aq_main.c`.

Dependencies/integration: used by Atlantic files needing open/close or work scheduling, and by XDP/ring paths checking the static key.

Risks: global static key must be incremented/decremented in balanced fashion or XDP locking behavior can be wrong across devices.

Test signals: compile, XDP attach/detach across multiple devices, and workqueue scheduling paths.
