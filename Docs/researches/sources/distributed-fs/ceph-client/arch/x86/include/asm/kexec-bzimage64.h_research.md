<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kexec-bzimage64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kexec-bzimage64.h

## Purpose
Declaration of the x86-64 bzImage kexec file loader operations. The header is 7 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_KEXEC_BZIMAGE64_H`

Notable declarations and inline helpers: `#define _ASM_KEXEC_BZIMAGE64_H`; `extern const struct kexec_file_ops kexec_bzImage64_ops;`

## Control Flow
No local control flow; the kexec file loader references kexec_bzImage64_ops to parse and load bzImage kernels.

## State and Persistence
State is kimage load metadata managed by kexec file code.

## Dependencies and Integration Points
Depends on CONFIG_KEXEC_FILE, bzImage parser, purgatory, and kexec.h architecture structures.

## Risks
Risks are compile/link breakage if ops are unavailable or loader ABI changes.

## Test Signals
Tests should load bzImage through kexec_file_load, verify signature/purgatory paths, and compile disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kexec-bzimage64.h -->
