<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/bitsperlong.h

Source read size: 13 lines, 302 bytes.

Purpose: selects userspace word size for PA-RISC headers. Important API: `__BITS_PER_LONG` is 64 under `__LP64__`, otherwise 32, then generic bits-per-long definitions are included. Control flow: preprocessor-only selection. State and persistence: ABI compile-time contract for structure layouts. Dependencies and integration points: used by IPC, signal, socket, and generic UAPI headers. Risks: incorrect LP64 detection changes layout of user-visible structs. Test signals: 32-bit and 64-bit headers_install, libc type-size checks, and ABI structure-size tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/bitsperlong.h -->
