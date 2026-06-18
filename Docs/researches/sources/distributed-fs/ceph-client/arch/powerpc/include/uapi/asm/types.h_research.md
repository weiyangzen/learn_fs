<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/types.h

Purpose: Selects PowerPC integer type model and defines aligned 128-bit vector storage for UAPI.

Important APIs/types/functions: Conditional include of `int-l64.h` for legacy ppc64 userspace unless `__SANE_USERSPACE_TYPES__`, otherwise `int-ll64.h`; `__vector128` as four `__u32` aligned to 16 bytes.

Control flow: Compile-time selection preserves old ppc64 long-based 64-bit type ABI for userspace while allowing sane ll64 opt-in.

State and persistence: No runtime state; controls ABI type sizes and vector register storage layout.

Dependencies and integration points: Depends on generic integer type headers and compiler alignment support.

Risks: Changing type model breaks userspace structures; vector alignment is required for VMX/VSX register sets.

Test signals: Headers compile with/without `__SANE_USERSPACE_TYPES__`, ppc64 type-size checks, and vector alignment tests.

Source read size: 41 lines, 1321 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/types.h -->
