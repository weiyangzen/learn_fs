# sources/distributed-fs/ceph-client/arch/s390/include/asm/mem_encrypt.h

Purpose: This header declares s390 memory encryption/decryption attribute APIs.

Important APIs/types/functions: `set_memory_encrypted(unsigned long vaddr, int numpages)` and `set_memory_decrypted(unsigned long vaddr, int numpages)` are exported for C code.

Control flow: Callers request page attribute transitions over a virtual address range; implementation code updates architecture-specific secure/encrypted state.

State and persistence: State persists in page attributes and protected/secure memory ownership, not in the header.

Dependencies and integration points: It integrates with protected virtualization, DMA sharing, and generic set-memory style code needing encrypted/decrypted transitions.

Risks and test signals: Incorrect transitions can expose protected memory or make shared buffers inaccessible. Tests should cover protected guest memory sharing, DMA bounce/shared pages, error handling, and non-assembler build coverage.
