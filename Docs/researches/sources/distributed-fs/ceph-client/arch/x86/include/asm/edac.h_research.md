
# sources/distributed-fs/ceph-client/arch/x86/include/asm/edac.h

Purpose: x86 EDAC atomic scrub helper.

Important APIs and control flow: `edac_atomic_scrub()` walks a memory range as 32-bit words and issues `lock addl $0` to each word, carefully forcing an atomic read-modify-write without changing the value.

State, dependencies, and risks: state is target memory and cache coherency observed by ECC hardware. Dependencies include callers passing valid, 4-byte-addressable memory. Risks include size truncation for non-multiple-of-four lengths, using on MMIO or invalid memory, and performance impact from locked operations. Test signals are EDAC scrub paths, ECC error-injection tests, and build coverage.
