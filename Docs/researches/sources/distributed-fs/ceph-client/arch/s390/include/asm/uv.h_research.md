## sources/distributed-fs/ceph-client/arch/s390/include/asm/uv.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/uv.h` is a Ultravisor protected-
virtualization interface in the s390 ceph-client Linux source snapshot. It has 641 lines and 16561
bytes; exported UAPI contract: no.

### Important APIs, Types, And Functions
UVC command codes, packed control blocks, feature bits, secure-guest lifecycle calls,
secret/attestation helpers, and secure/shared page conversion helpers
Important macros/constants: `_ASM_S390_UV_H`, `UVC_CC_OK`, `UVC_CC_ERROR`, `UVC_CC_BUSY`, `UVC_CC_PARTIAL`, `UVC_RC_EXECUTED`, `UVC_RC_INV_CMD`, `UVC_RC_INV_STATE`, `UVC_RC_INV_LEN`, `UVC_RC_NO_RESUME`, `UVC_RC_MORE_DATA`, `UVC_RC_NEED_DESTROY`, `UVC_CMD_QUI`, `UVC_CMD_QUERY_KEYS`, `UVC_CMD_INIT_UV`, `UVC_CMD_CREATE_SEC_CONF`, `UVC_CMD_DESTROY_SEC_CONF`, `UVC_CMD_DESTROY_SEC_CONF_FAST`, `UVC_CMD_CREATE_SEC_CPU`, `UVC_CMD_DESTROY_SEC_CPU`; plus 36 more.
Important types/layouts: `uv_cb_header`, `uv_cb_qui`, `uv_key_hash`, `uv_cb_query_keys`, `uv_cb_init`, `uv_cb_cgc`, `uv_cb_csc`, `uv_cb_cts`, `uv_cb_cfs`, `uv_cb_ssc`, `uv_cb_unp`, `uv_cb_cpu_set_state`, `for`, `uv_cb_nodata`, `uv_cb_destroy_fast`, `uv_cb_share`, `uv_cb_attest`, `uv_cb_dump_cpu`, `uv_cb_dump_stor_state`, `uv_cb_dump_complete`; plus 13 more.
Important declarations or inline helpers: `volatile`, `CC_TRANSFORM`, `test_bit_inv`, `share`, `uv_find_secret`, `uv_retrieve_secret`, `uv_pin_shared`, `uv_destroy_folio`, `uv_destroy_pte`, `uv_convert_from_secure_pte`, `s390_wiggle_split_folio`, `__make_folio_secure`, `uv_convert_from_secure`, `uv_convert_from_secure_folio`, `setup_uv`, `__uv_call`, `uv_call`, `uv_call_sched`, `uv_cmd_nodata`, `uv_list_secrets`; plus 5 more.

### Control Flow
Protected-virtualization callers fill an aligned control block, set a UVC command in the common
header, execute the Ultravisor call wrapper, then branch on condition code, response code, and
reason code. Page sharing helpers add memory-management state transitions around those calls.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
KVM protected virtualization, memory management, page sharing, attestation/secret drivers, and early
UV setup. Direct include dependencies detected here: `linux/types.h`, `linux/errno.h`,
`linux/bug.h`, `linux/sched.h`, `asm/page.h`, `asm/asm.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for KVM protected virtualization, memory
management, page sharing, attestation/secret drivers, and early UV setup. For UAPI files, the
integration point also includes headers_install and userspace programs compiled against the exported
layout.

### Risks
control-block layout or page-state bugs can leak protected guest memory or wedge secure guests

### Test Signals
PV guest lifecycle tests, UV query/secret/attestation tests, secure page conversion, and KVM
migration/dump paths
