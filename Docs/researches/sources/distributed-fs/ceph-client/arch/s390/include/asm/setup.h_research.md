## sources/distributed-fs/ceph-client/arch/s390/include/asm/setup.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/setup.h` is a s390 boot setup constants
and hooks in the s390 ceph-client Linux source snapshot. It has 105 lines and 2847 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
parmarea, lowcore startup offsets, machine flags, dump metadata, decompressor options, and early
console/fault helpers
Important macros/constants: `_ASM_S390_SETUP_H`, `PARMAREA`, `COMMAND_LINE_SIZE`, `LPP_MAGIC`, `LPP_PID_MASK`, `STARTUP_NORMAL_OFFSET`, `STARTUP_KDUMP_OFFSET`, `LEGACY_COMMAND_LINE_SIZE`, `ZLIB_DFLTCC_DISABLED`, `ZLIB_DFLTCC_FULL`, `ZLIB_DFLTCC_DEFLATE_ONLY`, `ZLIB_DFLTCC_INFLATE_ONLY`, `ZLIB_DFLTCC_FULL_DEBUG`, `CONSOLE_IS_UNDEFINED`, `CONSOLE_IS_SCLP`, `CONSOLE_IS_3215`, `CONSOLE_IS_3270`, `CONSOLE_IS_VT220`, `CONSOLE_IS_HVC`, `SET_CONSOLE_SCLP`; plus 4 more.
Important types/layouts: `parmarea`, `pt_regs`, `oldmem_data`.
Important declarations or inline helpers: `register_early_console`, `vmcp_cma_reserve`, `report_user_fault`, `void`, `gen_lpswe`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
IPL/startup assembly, boot command line parsing, kdump, VMCP CMA, and lowcore PSW loading. Direct
include dependencies detected here: `linux/bits.h`, `uapi/asm/setup.h`, `linux/build_bug.h`,
`asm/lowcore.h`, `asm/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for IPL/startup assembly, boot command line
parsing, kdump, VMCP CMA, and lowcore PSW loading. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
ABI-offset mismatches or command-line size drift can break early boot before diagnostics are
available

### Test Signals
boot variants for normal, kdump, z/VM, LPAR, and command-line edge cases
