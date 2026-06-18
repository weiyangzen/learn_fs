<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hypervisor.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/hypervisor.h

## Purpose
Common x86 hypervisor detection and initialization interface for VMware, Hyper-V, Xen, KVM, Jailhouse, ACRN, bhyve, and native mode. The header is 85 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/kvm_para.h>`; `#include <asm/x86_init.h>`; `#include <asm/xen/hypervisor.h>`

Notable constants/macros: `#define _ASM_X86_HYPERVISOR_H`

Notable declarations and inline helpers: `#define _ASM_X86_HYPERVISOR_H`; `enum x86_hypervisor_type {`; `struct hypervisor_x86 {`; `enum x86_hypervisor_type type;`; `struct x86_hyper_init init;`; `struct x86_hyper_runtime runtime;`; `bool ignore_nopv;`; `extern const struct hypervisor_x86 x86_hyper_vmware;`; `extern const struct hypervisor_x86 x86_hyper_ms_hyperv;`; `extern const struct hypervisor_x86 x86_hyper_xen_pv;`; `extern const struct hypervisor_x86 x86_hyper_kvm;`; `extern const struct hypervisor_x86 x86_hyper_jailhouse;`; `extern const struct hypervisor_x86 x86_hyper_acrn;`; `extern const struct hypervisor_x86 x86_hyper_bhyve;`; `extern struct hypervisor_x86 x86_hyper_xen_hvm;`; `extern bool nopv;`; `extern enum x86_hypervisor_type x86_hyper_type;`; `extern void init_hypervisor_platform(void);`; `static inline bool hypervisor_is_type(enum x86_hypervisor_type type)`; `static inline void init_hypervisor_platform(void) { }`

## Control Flow
init_hypervisor_platform() selects a detected hypervisor descriptor and applies init/runtime callbacks unless nopv disables paravirtualization for descriptors that honor it.

## State and Persistence
State is global x86_hyper_type, nopv, and registered hypervisor_x86 descriptors with init/runtime callback tables.

## Dependencies and Integration Points
Depends on kvm_para, x86_init, Xen hypervisor hooks, CPUID/vendor detection, and early boot init ordering.

## Risks
Risks include mis-detection, wrong callback ordering, nopv bypass for ignore_nopv descriptors, and native fallback behavior changing guest boot.

## Test Signals
Tests should boot native and each supported guest type, verify nopv behavior, CPUID detection, callback installation, and paravirt feature exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hypervisor.h -->
