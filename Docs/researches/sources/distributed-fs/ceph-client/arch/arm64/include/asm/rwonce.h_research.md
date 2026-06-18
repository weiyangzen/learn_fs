# sources/distributed-fs/ceph-client/arch/arm64/include/asm/rwonce.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/rwonce.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/rwonce.h` Overrides READ_ONCE under LTO to preserve address-dependency ordering with RCpc acquire loads on arm64. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
__LOAD_RCPC, __rwonce_typeof_unqual(), __READ_ONCE(), fallback include of asm-generic/rwonce.h. The file is 83 lines / 2399 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
For 1/2/4/8-byte loads under LTO, inline assembly emits ldar or alternative-patched ldapr depending on ARM64_HAS_LDAPR; other sizes fall back to volatile loads. Non-LTO and VDSO builds use the generic definitions.

### State, Persistence, And Dependencies
No persistent state; alternatives patch instruction choice based on CPU capabilities. Depends on compiler_types, alternative-macros, generic rwonce; used across the kernel anywhere READ_ONCE participates in dependency ordering.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Compiler or CPU reordering could break lockless algorithms; type-qualifier workarounds and asm constraints must keep thread-safety and aliasing diagnostics quiet.

### Test Signals
Build LTO/non-LTO, run LKMM/litmus-sensitive lockless tests, RCU stress, and LDAPR alternative patch coverage.
