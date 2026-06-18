# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_phyp.h

Purpose: Declares the eHEA PHYP ABI used by the driver: notification event masks, H_CALL control block layouts, selection masks, speed/receive-control constants, resource-operation prototypes, and EPA constructor/destructor helpers.

Important APIs and types: `hcp_epas_ctor()` maps hypervisor-provided resource pages into kernel virtual address space; `hcp_epas_dtor()` unmaps them. Control blocks `hcp_modify_qp_cb0`, `hcp_modify_qp_cb1`, `hcp_query_ehea`, and `hcp_ehea_port_cb0` through `cb7` model PHYP query/modify payloads. Masks such as `H_QPCB0_*`, `H_PORT_CB0_*`, `H_PORT_CB4_*`, `H_REGBCMC_*`, `NEQE_*`, and `NELR_*` define exact bitfields. Prototypes expose every wrapper implemented in `ehea_phyp.c`.

Control flow: `ehea_main.c` allocates a zeroed page for the relevant control block, fills selected fields, and calls query/modify wrappers with a category and selection mask. `ehea_phyp.c` packs the category, port number, resource handles, and physical control-block address into H_CALL registers. Notification event bits are parsed by `ehea_parse_eqe()` and reset through `ehea_h_reset_events()`.

State and persistence: The header defines data exchanged with firmware; it does not own state. `hcp_query_ehea` returns adapter capability state. Port control blocks reflect or request firmware state for MAC, receive control, VLAN filters, counters, jumbo/speed, promiscuous default queue, and default unicast queue.

Dependencies and integration: Depends on Linux delay, Power hypervisor call definitions, and eHEA core/hardware headers. It is the shared contract between the PHYP wrapper implementation and the main/QMR driver code.

Risks: Control block field ordering and selection masks are firmware ABI. Incorrect category/mask pairing can modify unrelated settings. `hcp_epas_ctor()` does pointer arithmetic on an `__iomem` mapping and assumes PAGE_SIZE/PAGE_MASK handling is correct for the platform. Speed constants must stay aligned with ethtool conversion and port sensing.

Test signals: Port attribute sensing, speed modification, VLAN filter changes, jumbo enable/query, promiscuous default-QPN changes, adapter capability query, NEQ event parsing, QP modify/query state transitions, and sparsemem builds validating control-block sizes.
