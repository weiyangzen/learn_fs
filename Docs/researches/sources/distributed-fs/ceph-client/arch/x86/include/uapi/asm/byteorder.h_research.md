<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/byteorder.h

Purpose: Selects little-endian byte-order definitions for x86 UAPI.

Important APIs/types/functions: Inclusion of `linux/byteorder/little_endian.h`.

Control flow: None beyond preprocessing.

State and persistence behavior: No runtime state. The header defines compile-time conversion behavior for userspace-visible structures.

Dependencies and integration points: Integrated with UAPI code that needs endian annotations and conversion helpers.

Risks and test signals: Risk is effectively limited to include/export breakage. Test `headers_install` and userspace compilation of endian helper consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/byteorder.h -->
