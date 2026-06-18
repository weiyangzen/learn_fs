<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/mgmt_util.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/mgmt_util.h

Purpose: defines internal management helper data structures and function prototypes shared by Bluetooth mgmt implementation files.

Important APIs/types/functions: `struct mgmt_pending_cmd` represents a pending asynchronous mgmt command with opcode, controller, copied parameters, socket, optional skb/user data, and completion callback. `struct mgmt_mesh_tx` represents a queued mesh transmission with socket, controller index, handle, instance, and a bounded command parameter buffer. The header declares all event, command reply, pending-command, and mesh-list helpers implemented in `mgmt_util.c`.

Control flow: no executable flow exists here. Callers allocate pending commands through `mgmt_pending_new`/`add`, later search, iterate, validate, remove, and free them through the declared helpers. Mesh callers use add/find/next/foreach/remove to sequence pending mesh sends.

State and persistence behavior: the structs describe transient in-memory state owned by `struct hci_dev` lists. Socket references are held for pending commands and mesh sends until removal. Mesh command storage is sized for `struct mgmt_cp_mesh_send` plus a 31-byte tail.

Dependencies and integration points: depends on list heads, sockets, sk_buffs, HCI devices, and mgmt mesh command definitions from the Bluetooth core include set. It is consumed by mgmt command handlers and HCI event completion paths.

Risks: struct layout is internal but ownership semantics are subtle; callers must respect list locking and avoid freeing pending commands still visible on `hdev->mgmt_pending`. The mesh parameter buffer is fixed-size, so callers must validate lengths before copying into it. Callback signatures imply completion can run with command state still attached unless caller removes carefully.

Test signals: build coverage plus mgmt async command tests, cancellation tests, mesh send queue tests, and lockdep around `mgmt_pending_lock` should exercise this header’s contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/mgmt_util.h -->
