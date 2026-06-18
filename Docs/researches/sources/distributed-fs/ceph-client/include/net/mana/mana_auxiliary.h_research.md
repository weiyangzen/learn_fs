<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/mana_auxiliary.h -->
# sources/distributed-fs/ceph-client/include/net/mana/mana_auxiliary.h

## Purpose
`mana_auxiliary.h` is a tiny bridge header defining the auxiliary-bus wrapper used to expose a MANA GDMA device as an auxiliary device.

## Important APIs, types, and functions
It includes `mana.h` and `<linux/auxiliary_bus.h>` and defines `struct mana_adev` with an embedded `struct auxiliary_device adev` and a pointer to the associated `struct gdma_dev`.

## Control flow
GDMA/MANA code can allocate or recover `mana_adev` around an auxiliary device so child drivers bind through the auxiliary bus while still reaching the GDMA device.

## State and persistence
It defines no behavior or persistence. Runtime state is the object lifetime of the auxiliary device and the referenced GDMA device.

## Dependencies and integration points
It depends on MANA core types and the Linux auxiliary bus. It integrates MANA Ethernet/RDMA child-device registration with the generic auxiliary-device framework.

## Risks and test signals
Risks are mostly lifetime-related: the embedded auxiliary device and `gdma_dev` pointer must remain valid across probe/remove and bus callbacks. Tests should cover auxiliary device registration, driver bind/unbind, and teardown ordering.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mana/mana_auxiliary.h` completely for this pass (10 lines, 223 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mana/mana_auxiliary.h -->
