# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/tcm_qla2xxx.h

Purpose: private data model for the qla2xxx target-core fabric module.

Important APIs/types: defines `TCM_QLA2XXX_NAMELEN`, `TCM_QLA2XXX_DEFAULT_TAGS`, `struct tcm_qla2xxx_nacl`, `struct tcm_qla2xxx_tpg_attrib`, `struct tcm_qla2xxx_tpg`, `struct tcm_qla2xxx_fc_loopid`, and `struct tcm_qla2xxx_lport`.

Control flow: these structures are allocated by configfs lport/TPG creation, populated during session setup, queried by target-core callbacks, and cleaned during TPG/lport removal. The lport contains both lookup structures needed by incoming firmware events: S_ID btree and loop-id array.

State and persistence: state includes WWPN/WWNN values, formatted WWN strings, NodeACL to `fc_port` links, target portal attributes, TPG enabled bit, pointer to qla VHA, and TPG=1 shortcut for physical mode. It persists for the lifetime of configfs fabric objects and active sessions.

Dependencies and integration: includes target-core base, Linux btree, and `qla_target.h`, tying fabric-level state to qla low-level target command/session structs.

Risks: fixed name buffer length, large vmalloc loop-id map allocation, stale `fc_port` pointers, TPG=1 assumption for non-NPIV mode, and synchronization requirements around lookup maps. Test signals include WWN formatting/parsing, lport allocation failure cleanup, session lookup by S_ID and loop ID, and configfs attribute visibility.
