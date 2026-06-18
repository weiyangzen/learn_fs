# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_cmds.h

Purpose: defines the firmware command ABI for the BE2 iSCSI driver: mailbox and MCC WRBs, completions, doorbells, queue contexts, async events, network/iSCSI management payloads, firmware configuration structures, CQE layouts, opcodes, statuses, and exported command-helper prototypes.

Important APIs/types/functions: core transport structures include `struct be_sge`, `struct be_mcc_wrb`, `struct be_mcc_compl`, and `struct be_mcc_mailbox`. Command headers are `be_cmd_req_hdr` and `be_cmd_resp_hdr`. Queue context requests cover EQ, CQ, MCCQ, default PDU queues, WRBQ, template pages, and SGL pages. Management structures cover CHAP/login options, session info, IP address records, gateway/VLAN, TCP connect/offload, invalidation, TCP upload, firmware config, and port name. CQE structures include solicited and driver-message variants plus masks for parsing status, CID, WRB index, residuals, and validity. Prototypes expose all command helpers implemented in `be_cmds.c`.

Control flow: this header is declarative, but its constants drive all firmware interactions. Callers build a WRB, choose a subsystem/opcode, set request length and version, populate payload-specific structures, convert contexts to little endian where needed, post through mailbox or MCC, then parse completion/status fields using the masks defined here.

State and persistence: the structures describe transient command payloads and firmware-owned resources. Some commands create durable firmware objects for the life of the HBA function, such as queue IDs, CID/ICD ranges, and network interface settings. Completion codes and async events update driver state in other files.

Dependencies and integration: depends on iSCSI naming and kernel types made visible through including files. It is included from `be.h` and therefore sits at the center of command exchange among `be_cmds.c`, `be_mgmt.c`, `be_main.c`, and `be_iscsi.c`.

Risks and test signals: this file is layout-sensitive; field size, packing, endian conversion, and opcode values must match firmware. BE2/BE3 and newer chips use different context versions for some commands. The duplicated opcode names for common/iSCSI domains require correct subsystem pairing. Test signals are compile-time size/layout checks where available, successful firmware queue creation on each supported chip generation, network config commands, TCP offload/invalidate/upload, async link/SLI events, and solicited CQE parsing for normal and error completions.
