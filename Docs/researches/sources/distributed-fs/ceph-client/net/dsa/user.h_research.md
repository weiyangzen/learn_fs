# sources/distributed-fs/ceph-client/net/dsa/user.h

Purpose: local interface for DSA user-device support. It defines the per-user private data layout and exposes lifecycle, notifier, VLAN, MTU, conduit, and tagger helpers to other DSA core files.

Important APIs/types: `struct dsa_user_priv` stores cached tagger xmit callback, GRO cells, owning `struct dsa_port *dp`, optional netpoll, and TC matchall state. Extern notifier blocks expose switchdev notifier instances. Function declarations cover MII init, create/destroy, suspend/resume, notifier registration, host unicast install/uninstall, host address sync/unsync, tagger setup, MTU changes, conduit changes, and VLAN filtering management. Inline helpers `dsa_user_to_port()` and `dsa_user_to_conduit()` translate netdevs to DSA state.

Control flow: other DSA modules include this header to interact with user netdevs without knowing the implementation details in `user.c`. The inline helpers are hot-path utilities used heavily by taggers and TX/RX code.

State and persistence: the header defines runtime netdev-private state but owns no persistent state.

Dependencies and integration: includes bridge, VLAN, list, netpoll, DSA, and GRO headers. It is a central contract between DSA user-device handling, taggers, switch code, and netdevice notifiers.

Risks and test signals: changing `struct dsa_user_priv` affects netdev private layout and tagger hot paths. Tests should compile all taggers and DSA core users, and runtime tests should verify `dsa_user_to_port()` assumptions for every DSA user netdev.
