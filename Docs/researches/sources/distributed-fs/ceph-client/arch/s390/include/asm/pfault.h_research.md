# sources/distributed-fs/ceph-client/arch/s390/include/asm/pfault.h

Purpose: This header wraps s390 pseudo-page-fault initialization for optional `CONFIG_PFAULT` support.

Important APIs/types/functions: `__pfault_init()`, `__pfault_fini()`, `pfault_init()`, and `pfault_fini()` are defined; the public wrappers return `-EOPNOTSUPP` or no-op when the feature is disabled.

Control flow: Initialization code calls `pfault_init()` to enable host/hypervisor pseudo-page-fault handling and `pfault_fini()` during teardown.

State and persistence: Persistent state is maintained by the implementation and hypervisor registration, not the header.

Dependencies and integration points: It depends on Linux errno and integrates with s390 virtualization paging notifications and KVM/zVM-style pfault handling.

Risks and test signals: Callers must handle disabled support cleanly. Tests should include CONFIG_PFAULT on/off builds, init/fini idempotence, page-fault notification delivery under virtualization, and fallback on unsupported machines.
