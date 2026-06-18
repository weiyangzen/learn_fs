# sources/distributed-fs/ceph-client/arch/mips/include/asm/ftrace.h


### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/ftrace.h` MIPS ftrace call-site metadata, safe text/stack access, and syscall symbol matching. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 110 lines / 2771 bytes. macros/constants: `_ASM_MIPS_FTRACE_H`, `MCOUNT_ADDR`, `MCOUNT_INSN_SIZE`, `mcount`, `safe_load`, `safe_store`, `safe_load_code`, `safe_store_code`, `safe_load_stack`, `safe_store_stack`, `ARCH_HAS_SYSCALL_MATCH_SYM_NAME`; types/functions/declarations: `extern void _mcount(void);`, `static inline unsigned long ftrace_call_adjust(unsigned long addr)`, `struct dyn_arch_ftrace {`, `static inline bool arch_syscall_match_sym_name(const char *sym,`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: no direct includes.

### Integration Points
Used by dynamic tracing and runtime text patching. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Bad instruction sizing or safe access can patch the wrong code and crash. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
