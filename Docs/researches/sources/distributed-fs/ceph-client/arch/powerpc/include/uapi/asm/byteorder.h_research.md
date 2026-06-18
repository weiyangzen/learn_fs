<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/byteorder.h

Purpose: Selects PowerPC userspace byteorder helpers for little- or big-endian builds.

Important APIs/types/functions: Includes `linux/byteorder/little_endian.h` when `__LITTLE_ENDIAN__` is set, otherwise big-endian helpers.

Control flow: Compile-time include selection provides conversion macros to userspace/kernel UAPI consumers.

State and persistence: No runtime state; affects compile-time endian conversions.

Dependencies and integration points: Depends on compiler/endian defines and Linux byteorder headers.

Risks: Wrong include corrupts multibyte UAPI field interpretation on cross-endian builds.

Test signals: Headers compile for powerpc64le and big-endian powerpc plus byte-swap macro unit checks.

Source read size: 17 lines, 550 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/byteorder.h -->
