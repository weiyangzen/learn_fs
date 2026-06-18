# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mem_encrypt.h

Purpose: exposes PowerPC secure-guest memory encryption/decryption hooks and DMA policy.

Important APIs/types/functions: `force_dma_unencrypted(struct device *dev)` returns `is_secure_guest()`. `set_memory_encrypted()` and `set_memory_decrypted()` are declared for changing page encryption state.

Control flow: DMA mapping code can force unencrypted bounce/accessible memory for secure guests, while memory-management code calls encryption/decryption setters for page ranges.

State and persistence: encryption state is page-level platform state changed by implementation files or ultravisor/firmware interactions. This header stores no state.

Dependencies and integration points: includes `asm/svm.h` and Linux types; integrates secure virtual machine support with DMA and memory attribute management.

Risks: returning the wrong DMA policy can expose encrypted memory to devices that cannot access it or leak plaintext. Page encryption transitions must be synchronized with mappings and device access.

Test signals: secure guest boot, DMA to/from devices in secure guests, page encryption/decryption tests, and non-secure guest checks that DMA policy remains unchanged.
