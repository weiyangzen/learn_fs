# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/svm.c

Purpose: Implements pSeries secure guest memory-sharing hooks for SWIOTLB, generic set-memory encrypted/decrypted calls, and dispatch trace log page sharing.

Important APIs/types/functions: Provides early init `init_svm()`, `set_memory_encrypted()`, `set_memory_decrypted()`, `dtl_cache_ctor()`, and DTL shared-page tracking helpers.

Control flow: Early init checks `is_secure_guest()`, forces SWIOTLB use for DMA, marks SWIOTLB usable for any address, and shares the SWIOTLB buffer with the host. Encryption/decryption hooks validate page alignment and call ultravisor unshare/share operations when confidential-computing memory encryption is active. DTL cache construction shares each dispatch log page once.

State and persistence: Maintains a fixed array of shared DTL pages and a count. SWIOTLB flags are global runtime state. Memory sharing state is maintained by the ultravisor.

Dependencies and integration points: Depends on secure guest detection, confidential-computing attributes, ultravisor page share/unshare calls, SWIOTLB, DTL allocation from `setup.c`, and machine early init ordering.

Risks: DTL page tracking has no explicit locking and assumes construction context serialization. `dtl_nr_pages` overflow only warns after storing. Encryption hooks silently no-op outside encrypted guests, so callers must not infer security transitions there.

Test signals: Secure guest boot DMA with SWIOTLB forced, set_memory encrypted/decrypted alignment checks, ultravisor share/unshare calls, DTL allocation across all CPUs, and non-secure guest no-op behavior.

Source read size: 95 lines, 2335 bytes.
