## sources/distributed-fs/ceph-client/include/linux/cc_platform.h

**Purpose:** This header declares a generic confidential-computing platform capability query interface.

**Important APIs/types/functions:** `enum cc_attr` lists active platform attributes such as host/guest memory encryption, guest state encryption, string I/O unrolling, SEV-SNP, TDX, memory acceptance requirements, and host SNP. The primary API is `cc_platform_has(enum cc_attr attr)` declared later in the header implementation surface.

**Control flow, state, persistence:** Callers query whether a security/platform attribute is active before choosing memory, I/O, and virtualization behavior. State is derived from architecture/platform initialization, not stored by this header.

**Dependencies/integration:** Depends on generic types and architecture confidential-computing backends. Used by x86/arm64 memory encryption, DMA, I/O, and virtualization-sensitive code.

**Risks and test signals:** Risks include treating attributes as compile-time constants, assuming one vendor feature implies another, and missing fallbacks for encrypted guests. Test signals include architecture CC boot tests, SEV/TDX/SNP guest runs, memory acceptance tests, and compile coverage on non-CC architectures where queries return false.
