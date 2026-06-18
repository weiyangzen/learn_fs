## sources/distributed-fs/ceph-client/arch/s390/include/asm/scsw.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/scsw.h` is a subchannel status word
decoding in the s390 ceph-client Linux source snapshot. It has 1051 lines and 25665 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
packed command-mode, transport-mode, and EADM SCSW layouts plus inline accessors, validators, status
predicates, and mutators
Important macros/constants: `_ASM_S390_SCSW_H_`, `SCSW_FCTL_CLEAR_FUNC`, `SCSW_FCTL_HALT_FUNC`, `SCSW_FCTL_START_FUNC`, `SCSW_ACTL_SUSPENDED`, `SCSW_ACTL_DEVACT`, `SCSW_ACTL_SCHACT`, `SCSW_ACTL_CLEAR_PEND`, `SCSW_ACTL_HALT_PEND`, `SCSW_ACTL_START_PEND`, `SCSW_ACTL_RESUME_PEND`, `SCSW_STCTL_STATUS_PEND`, `SCSW_STCTL_SEC_STATUS`, `SCSW_STCTL_PRIM_STATUS`, `SCSW_STCTL_INTER_STATUS`, `SCSW_STCTL_ALERT_STATUS`, `DEV_STAT_ATTENTION`, `DEV_STAT_STAT_MOD`, `DEV_STAT_CU_END`, `DEV_STAT_BUSY`; plus 36 more.
Important types/layouts: `cmd_scsw`, `tm_scsw`, `eadm_scsw`, `scsw`.
Important declarations or inline helpers: `scsw_tm_is_valid_actl`, `scsw_cmd_is_valid_actl`, `scsw_tm_is_valid_cc`, `scsw_cmd_is_valid_cc`, `scsw_tm_is_valid_cstat`, `scsw_cmd_is_valid_cstat`, `scsw_tm_is_valid_dstat`, `scsw_cmd_is_valid_dstat`, `scsw_tm_is_valid_ectl`, `scsw_cmd_is_valid_ectl`, `scsw_tm_is_valid_eswf`, `scsw_cmd_is_valid_eswf`, `scsw_tm_is_valid_fctl`, `scsw_cmd_is_valid_fctl`, `scsw_tm_is_valid_key`, `scsw_cmd_is_valid_key`, `scsw_tm_is_valid_pno`, `scsw_cmd_is_valid_pno`, `scsw_tm_is_valid_stctl`, `scsw_cmd_is_valid_stctl`; plus 36 more.

### Control Flow
Callers receive an SCSW from channel hardware, use scsw_is_tm() to choose command versus transport
layout, then route all status queries through common accessors. Validator helpers check architected
masks before recovery code interprets activity, function, device, and subchannel status.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
common I/O, DASD/QETH/channel drivers, interrupt response blocks, and channel-status recovery paths.
Direct include dependencies detected here: `linux/types.h`, `asm/css_chars.h`, `asm/dma-types.h`,
`asm/cio.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for common I/O, DASD/QETH/channel drivers,
interrupt response blocks, and channel-status recovery paths. For UAPI files, the integration point
also includes headers_install and userspace programs compiled against the exported layout.

### Risks
bitfield or mode-detection errors misinterpret channel status, causing lost interrupts, bogus
residual counts, or incorrect recovery

### Test Signals
channel I/O status decoding tests, DASD/QETH error injection, and transport-mode FCX coverage
