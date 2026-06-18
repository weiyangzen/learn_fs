# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ocrdma/ocrdma_ah.h

Purpose: declares ocrdma address-handle constants and verbs/MAD entry points.

Important APIs/types/functions: defines bit masks and shifts for userspace AH ids: `OCRDMA_AH_ID_MASK`, VLAN-valid mask/shift, and L3 type mask/shift. Declares `ocrdma_create_ah`, `ocrdma_destroy_ah`, `ocrdma_query_ah`, and `ocrdma_process_mad`.

Control flow: no executable control flow; implementation lives in `ocrdma_ah.c`.

State and persistence: constants define how AH metadata is packed into the user context AH table, combining hardware AV id, optional L3 type, and VLAN-valid information.

Dependencies and integration: included by ocrdma verbs registration code and `ocrdma_ah.c`; function prototypes use RDMA core types (`ib_ah`, `rdma_ah_init_attr`, `rdma_ah_attr`, `ib_device`, MAD structures).

Risks: masks and shifts are part of the implicit userspace/kernel ABI for AH table entries. Changing them without coordinating userspace/provider code would break address-vector lookup.

Test signals: compile coverage, userspace AH creation with UDP encapsulation and VLAN, and validation that packed AH table values are decoded correctly by consumers.
