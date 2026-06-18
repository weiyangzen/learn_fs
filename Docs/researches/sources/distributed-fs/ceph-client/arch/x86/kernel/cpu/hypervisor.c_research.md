# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/hypervisor.c

Purpose: detects the active x86 hypervisor early and installs hypervisor-specific platform hooks.

Important APIs and flow: the static `hypervisors[]` table lists configured providers, including Xen, VMware, Hyper-V, KVM, Jailhouse, ACRN, and bhyve. The `nopv` early parameter suppresses paravirtual provider selection unless a provider declares `ignore_nopv`. `detect_hypervisor_vendor()` calls each provider's `detect()` method, keeps the highest priority match, and logs the provider name. `init_hypervisor_platform()` copies non-NULL init/runtime hook arrays from the selected provider into `x86_init.hyper` and `x86_platform.hyper`, sets exported `x86_hyper_type`, and calls the selected `init_platform()` hook.

State and persistence: global boot-time state consists of `nopv`, `x86_hyper_type`, and copied function pointers in x86 platform initialization structures. There is no persistence beyond the running kernel.

Dependencies and integration: depends on provider `struct hypervisor_x86` implementations and the x86 platform hook tables used by time, interrupt, memory, and paravirtual subsystems.

Risks and test signals: detection priority conflicts or `nopv` handling can change boot behavior under nested virtualization. Signals include early boot hypervisor logs, exported hypervisor type, paravirtual feature availability, and boot tests across supported guests with and without `nopv`.
