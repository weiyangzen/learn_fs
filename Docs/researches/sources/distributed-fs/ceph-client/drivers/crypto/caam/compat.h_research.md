<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/compat.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/compat.h

Purpose: central compatibility include for CAAM driver sources. It pulls common Linux, networking, DMA, OF, crypto API, and algorithm headers into CAAM compilation units.

Important APIs and control flow: this header defines no functions, state, or macros beyond the include guard. Its practical API is transitive: CAAM files include `compat.h` to gain declarations for `struct device`, interrupts, platform/OF helpers, DMA mapping, IOMMU, spinlocks, debugfs, circular buffers, clocks, XFRM, and crypto framework types such as skcipher, aead, hash, akcipher, RSA, AES, DES, GCM, SHA, MD5, ChaCha, and Poly1305.

State and persistence behavior: none. It affects compile-time dependency visibility only.

Dependencies and integration points: included by controller, RNG, JR, QI, error, and key-generation code. It reduces per-file include verbosity but also couples unrelated CAAM modules to a broad header surface.

Risks and test signals: risks are hidden dependencies, slower incremental builds, accidental reliance on indirect includes, and harder include hygiene when kernel APIs move. Test signals are successful allmodconfig-style CAAM builds and the ability to remove unnecessary direct/indirect headers only with full CAAM API coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/compat.h -->
