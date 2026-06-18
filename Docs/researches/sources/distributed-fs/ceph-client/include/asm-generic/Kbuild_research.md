# sources/distributed-fs/ceph-client/include/asm-generic/Kbuild

Purpose: Lists mandatory generic asm headers that every architecture except UML must provide or inherit, forming the baseline architecture ABI expected by the Linux kernel.

Important APIs, types, and functions: Uses Kbuild variable `mandatory-y` to require headers such as `atomic.h`, `archrandom.h`, `barrier.h`, `bitops.h`, `uaccess.h`, `io.h`, `irq.h`, `module.h`, `pgalloc.h`, `rwonce.h`, `tlbflush.h`, `topology.h`, and many others.

Control flow: Kbuild consumes this file while preparing/generated checking architecture include trees. UML is excluded because it borrows several asm headers from the host architecture.

State and persistence: No runtime state. It persists build-system policy about required architecture header coverage.

Dependencies and integration points: Integrates with arch header generation, generic header fallbacks, `make headers_check`-style validation, and architecture port bring-up.

Risks and test signals: Risks are missing mandatory headers in new ports, adding headers here without compatible generic fallbacks, or breaking UML assumptions. Test all-arch/header builds, new architecture defconfigs, and include dependency scanning.
