## sources/distributed-fs/ceph-client/arch/loongarch/kernel/relocate_kernel.S

### Purpose
`relocate_kernel.S` is the kexec relocation stub copied to a safe low-memory control page. It interprets the generic kexec indirection page list, copies source pages to destination pages, synchronizes caches/barriers, and jumps to the new kernel. Under SMP it also provides the secondary CPU mailbox wait loop.

### Important APIs, Types, And Functions
Defined symbols are `relocate_new_kernel`, optional `kexec_smp_wait`, and data symbol `relocate_new_kernel_size`. The entry ABI passes EFI boot flag, command line pointer, system table pointer, start address, and first indirection entry in `a0..a4`.

### Control Flow
The stub saves the indirection pointer in `s0`; crash kernels with no indirection jump directly to `done`. Otherwise it loops over entries, updating destination address for `IND_DESTINATION`, switching list pages for `IND_INDIRECTION`, terminating on `IND_DONE`, and copying one page word-by-word for `IND_SOURCE`. The `done` path executes `ibar` and `dbar`, then jumps to `a3` preserving boot arguments. Secondary CPUs poll `LOONGARCH_IOCSR_MBUF0`, convert the mailbox PC to cached address space, and jump to it.

### State, Persistence, And Dependencies
The stub mutates physical memory at destination pages and relies on the copied control page remaining executable. It depends on generic kexec entry flag encodings, page size constants, LoongArch IOCSR mailbox, and cached address-space layout.

### Integration Points
`machine_kexec_prepare` copies this code and records its size; `machine_kexec` passes converted indirection entries. SMP shutdown sends secondaries into the relocated `kexec_smp_wait`.

### Risks
The copy loop assumes whole-page copies and correct virtual address conversion before entry. Cache/barrier sequencing is critical before entering the new kernel. The secondary mailbox polling loop can spin forever if firmware or boot CPU never writes a PC.

### Test Signals
Normal kexec with multiple source/destination/indirection pages, crash-kexec direct-entry path, SMP secondary restart, and page-size configuration changes should be tested. Early boot failures in the next kernel often indicate bad copy or stale I-cache.
