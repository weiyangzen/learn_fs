<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/mgmt_config.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/mgmt_config.h

Purpose: declares the default system and runtime configuration mgmt command handlers implemented by `mgmt_config.c`.

Important APIs/types/functions: exposes `read_def_system_config`, `set_def_system_config`, `read_def_runtime_config`, and `set_def_runtime_config`, all with the standard mgmt handler signature using `struct sock *`, `struct hci_dev *`, request data, and request length.

Control flow: this header has no executable flow. The mgmt dispatcher includes it so opcode handling tables can call the configuration handlers.

State and persistence behavior: owns no state. The declared functions operate on `struct hci_dev` runtime configuration and reply over the mgmt socket.

Dependencies and integration points: relies on including contexts to provide declarations for `struct sock`, `struct hci_dev`, and integer types. It is an internal Bluetooth mgmt header, not a stable userspace ABI.

Risks: prototype drift from `mgmt_config.c` or mgmt dispatcher expectations would break builds. Because the header carries no include guard in this snapshot, repeated inclusion would rely on C allowing duplicate compatible function declarations.

Test signals: build coverage of `net/bluetooth` is the primary signal; command dispatch tests indirectly verify each prototype is wired to the correct opcode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/mgmt_config.h -->
