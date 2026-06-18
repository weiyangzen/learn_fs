## sources/distributed-fs/ceph-client/arch/arm64/kernel/vmcore_info.c

### Purpose
`vmcore_info.c` exports ARM64 crash-dump metadata needed by makedumpfile/crash tooling to interpret a vmcore.

### Important APIs, Types, And Functions
It defines `arch_crash_save_vmcoreinfo` and helper `get_tcr_el1_t1sz`.

### Control Flow
During crash vmcoreinfo collection, the function records VA bits, module/vmalloc/vmemmap ranges, `kimage_voffset`, `PHYS_OFFSET`, current `TCR_EL1.T1SZ`, KASLR offset, and the kernel pointer-auth PAC mask when address authentication is supported.

### State, Persistence, And Dependencies
The output is appended to the vmcoreinfo note captured with the crash dump. It reads live system registers and architecture constants but owns no normal runtime state.

### Integration Points
Used by kexec/crash dump infrastructure, ARM64 memory layout code, pointer authentication helpers, and userspace crash analysis tools.

### Risks
Incorrect metadata makes vmcore virtual-to-physical translation, module lookup, vmemmap decoding, or PAC stripping fail. Format details such as hex string output are consumed by external tools.

### Test Signals
Trigger kdump, inspect vmcoreinfo notes, verify crash/makedumpfile can resolve kernel symbols and memory with KASLR, different VA sizes, and pointer-auth enabled builds.
