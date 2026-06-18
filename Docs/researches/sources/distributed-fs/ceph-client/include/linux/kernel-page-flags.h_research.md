# sources/distributed-fs/ceph-client/include/linux/kernel-page-flags.h

## Purpose
Extends the UAPI kernel page flag list with kernel-only diagnostic flag numbers for page owner/private/architecture/debug state.

## Important APIs, Types, And Functions
After including `uapi/linux/kernel-page-flags.h`, it defines kernel hacking flags such as `KPF_RESERVED`, `KPF_MLOCKED`, `KPF_OWNER_2`, `KPF_PRIVATE`, `KPF_PRIVATE_2`, `KPF_OWNER_PRIVATE`, `KPF_ARCH`, `KPF_SOFTDIRTY`, `KPF_ARCH_2`, and `KPF_ARCH_3`.

## Control Flow
No runtime logic is present. Other code maps page state into these flag numbers when presenting page flags.

## State And Persistence
No state is stored in the header. The flags describe transient page state in memory.

## Dependencies And Integration Points
Depends on the UAPI page flag definitions. Integrates with `/proc/kpageflags`, memory debugging, page owner diagnostics, and architecture-specific page state reporting.

## Risks
The comment warns these kernel hacking flags are subject to change; userspace should not rely on them as stable ABI. Misnumbering can mislead memory diagnostic tools.

## Test Signals
Signals include `/proc/kpageflags` decoding tests, page owner/debug configurations, architecture flag coverage, and documentation/tooling checks that do not treat these as stable ABI.
