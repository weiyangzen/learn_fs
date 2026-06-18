# sources/distributed-fs/ceph-client/arch/s390/include/asm/msi.h

Purpose: This header adapts generic MSI support for s390 and declares MSI isolation behavior.

Important APIs/types/functions: It includes `asm-generic/msi.h` and defines `arch_is_isolated_msi()` as true with a note about s390 not using irq_domain in the same way as other architectures.

Control flow: Generic MSI code queries the predicate while configuring MSI isolation; s390 reports isolation even though userspace may still trigger MSIs within the same GISA.

State and persistence: There is no local state; MSI routing state lives in zPCI/adapter interrupt code.

Dependencies and integration points: It integrates generic MSI core with s390 zPCI/GISA interrupt behavior.

Risks and test signals: The isolation semantics are weaker than some architectures, so passthrough/security tests must account for same-GISA exposure. Tests should cover MSI allocation, VFIO/zPCI passthrough, interrupt remapping assumptions, and non-irqdomain paths.
