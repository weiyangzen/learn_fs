<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/byteorder.h

Purpose: selects SH user ABI byte-order helpers.

Important APIs/types/functions: includes little- or big-endian linux byteorder headers based on `__LITTLE_ENDIAN__`.

Control flow: compile-time dispatch only.

State and persistence: no runtime state.

Dependencies/integration: used by userspace and kernel UAPI consumers for endian conversions.

Risks: incorrect endian macro selection corrupts protocol and structure interpretation.

Test signals: compile headers for little and big endian SH targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/uapi/asm/byteorder.h -->
