<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/relocate_kernel.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/relocate_kernel.S

### Purpose
`relocate_kernel.S` is the PA-RISC kexec relocation stub that copies relocation entries in physical mode and jumps to the new kernel.

### Important APIs, Types, And Functions
It exports `relocate_new_kernel`, `relocate_new_kernel_size`, and kexec parameter slots plus offsets for command line, initrd start/end, and free memory.

### Control Flow
The stub disables interrupts and the Q bit, uses RFI to continue without translation, walks the kimage indirection list, handles done/indirection/destination/source entries, copies each page with register-sized loads and stores, flushes data/instruction caches, then branches to the new kernel start with kexec boot parameters.

### State, Persistence, And Dependencies
The only persistent state is the embedded kexec parameter words patched by the kexec setup path. Dependencies include `kimage->head` entry encoding, PA-RISC PSW/RFI control, cache flush instructions, and page-size constants.

### Integration Points
Used by the generic kexec/kdump path when transferring control to a replacement or crash kernel.

### Risks
Physical-mode relocation cannot rely on normal kernel services. Entry flag interpretation, register width, and cache coherency must be exact or the new kernel receives corrupted pages or parameters.

### Test Signals
Exercise normal kexec and crash-kernel kdump on 32-bit and 64-bit builds, with initrd/cmdline parameters and memory layouts requiring indirection entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/relocate_kernel.S -->
