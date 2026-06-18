# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_bond.h

Purpose: Declares the RoCE bonding data model, state machine enums, constants, and public hooks used by the HNS RoCE driver and HNS3 client glue.

Important APIs/types/functions: Constants limit a bond to four functions and two groups per bus. `struct hns_roce_bond_group` stores upper netdev, main device, active/slave maps, bond ID, bus, per-function netdev/handle pairs, readiness, bond state, LAG TX/hash mode, mutex, notifier, and delayed work. `struct hns_roce_die_info` stores per-bus groups, ID mask, mutex, and suspend count. Public functions cover lookup, allocation, cleanup, active-state check, init, suspend, and resume.

Control flow: The header supports the implementation's state machine: not attached, not bonded, bonded, slave-number change, and slave-state change. Command types distinguish set, change, and clear bond hardware operations.

State and persistence: All persistent bonding state is represented by the two structs here and is keyed by bus in the C file's global xarray.

Dependencies and integration: Includes `linux/netdevice.h` and `net/bonding.h`, and references HNS RoCE and HNAE3 handles through forward-visible structs from included headers. It is consumed by main/HNS3 lifecycle code and the bond implementation.

Risks: Constant limits are hardware policy; exceeding function or group counts produces unsupported behavior. Public hooks must be called in the right device/reset ordering. Test signals include compile coverage with bonding enabled, state enum handling in switch statements, and matching command enum values with firmware expectations.
