# sources/distributed-fs/ceph-client/include/xen/xen.h

## Purpose
`include/xen/xen.h` is the Linux-side Xen environment header. It exposes whether the kernel is native, PV, HVM, PVH, or initial domain, declares Xen boot flags and PVH start info, and provides allocation and mergeability helpers that abstract Xen memory behavior.

## Important APIs, Types, and Functions
Key definitions are `enum xen_domain_type`, `xen_domain_type`, `xen_pvh`, `xen_pv_domain()`, `xen_domain()`, `xen_hvm_domain()`, `xen_pvh_domain()`, `xen_initial_domain()`, `xen_start_flags`, `xen_pv_pci_possible`, `pvh_start_info`, `xen_prepare_pvh()`, `xen_pv_evtchn_do_upcall()`, `xen_biovec_phys_mergeable()`, `xen_alloc_unpopulated_pages()`, `xen_free_unpopulated_pages()`, `arch_xen_unpopulated_init()`, and `xen_processor_present()`.

## Control Flow
Boot code sets domain type and flags; later code branches through inline predicates to select Xen-specific paths. Unpopulated page helpers use dedicated unpopulated allocation when configured, otherwise fall back to ballooned pages. Dom0-only `xen_initial_domain()` checks `SIF_INITDOMAIN`.

## State and Persistence Behavior
Global domain type, PVH flag, start flags, PVH start info, saved max memory, and unpopulated page counters persist for the kernel lifetime. The header primarily exposes state managed elsewhere.

## Dependencies and Integration Points
It depends on Linux types, x86 feature detection, Xen HVM start-info UAPI, ballooning, ACPI/dom0 conditionals, and architecture hypervisor headers. It is included across block, memory, event-channel, ACPI, and Xen driver code.

## Risks and Test Signals
Risks include compile-time stubs masking unsupported paths, `BUG()` in `xen_processor_present()` when called without dom0 ACPI support, wrong domain predicate decisions, and fallback balloon allocation differences. Test signals include native/PV/HVM/PVH boot builds, dom0 detection, unpopulated page allocation, block bio merge behavior, and ACPI processor presence checks.
