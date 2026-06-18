<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/module.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/module.h

## Purpose
`module.h` stubs kernel module APIs needed by tools and lockdep code.

## APIs And Flow
It defines `module_param(name, type, perm)` as an empty macro and provides `__is_module_percpu_address()` returning `false`. There is no module registration or parameter parsing flow.

## State, Dependencies, Risks, Tests
There is no module state. It depends on `bool` being available through included context. Integration is with code shared from the kernel that annotates module parameters or checks module per-cpu address ranges. Risks are silently disabling module-specific behavior in tools and losing diagnostics for addresses that would be module-owned in-kernel. Tests should build shared code with module annotations and verify address classification callers handle `false`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/module.h -->
