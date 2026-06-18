
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/policy.c

Purpose: configfs policy manager for STM master/channel allocation. It lets users bind one STM device to one framing protocol and create named policy nodes containing allowed master/channel ranges and protocol-specific attributes.

Important APIs/types/functions: `struct stp_policy` links a configfs group to an STM device. `struct stp_policy_node` stores range limits and protocol-private data. Exported helpers include `stp_policy_node_priv()`, `to_pdrv_policy_node()`, `stp_policy_node_get_ranges()`, `stp_policy_unbind()`, `stp_policy_node_lookup()`, `stp_policy_node_put()`, `stp_configfs_init()`, and `stp_configfs_exit()`. `get_policy_node_type()` merges generic and protocol-specific configfs attributes.

Control flow: configfs root `stp-policy` accepts group names shaped like `<device>[:<protocol>].<policy>`. Creation finds the STM device, looks up the protocol, ensures no policy is already bound to that STM, stores protocol/device references, and initializes the policy group. Child groups create `stp_policy_node` objects with default full device ranges and protocol-private initialization. Attribute writes validate ranges against the bound STM device. Lookup walks slash-separated policy node names while holding the configfs subsystem mutex, returning a referenced node for allocation.

State and persistence: configfs objects are in-kernel state controlled by userspace directory operations. A policy holds references to the STM device and protocol until unbound/released. Policy-node private data persists while the configfs node exists.

Dependencies and integration: depends on STM core device/protocol lookup, configfs, module refs, and protocol attribute composition. `core.c` calls lookup/put while assigning outputs.

Risks: one-policy-per-STM enforcement means conflicting configfs groups must fail cleanly. Locking with configfs `su_mutex` and STM `policy_mutex` protects device/protocol links; order changes can deadlock. Policy release currently returns before `kfree(policy)` when already unbound, which should be checked for leak potential. Node lookup keeps the subsystem mutex held until `stp_policy_node_put()`, so callers must always put.

Test signals: create valid/invalid policy names, explicit and fallback protocols, nested nodes, range updates at boundaries, output assignment by node path, policy removal while sources are linked, and leak/lockdep tests around unbind/release.
