# sources/distributed-fs/ceph-client/drivers/interconnect/mediatek/icc-emi.h

Purpose: shared MediaTek EMI interconnect descriptor contract.

Important APIs/types/functions: `struct mtk_icc_node` contains node name, endpoint type, ID, aggregate state, and flexible link array. `struct mtk_icc_desc` wraps a node pointer array and count. Prototypes expose common probe/remove helpers.

Control flow: SoC topology files instantiate descriptors; `icc-emi.c` consumes them during platform probe.

State and persistence: aggregate fields are mutable static data and persist for module lifetime.

Dependencies/integration: platform drivers and interconnect core through including C files.

Risks and test signals: test flexible-array initializers, endpoint semantics, and remove/reprobe behavior with static mutable aggregate fields.
