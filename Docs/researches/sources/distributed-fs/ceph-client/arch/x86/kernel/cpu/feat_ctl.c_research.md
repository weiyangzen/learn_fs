# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/feat_ctl.c

Purpose: manages Intel `IA32_FEAT_CTL` policy during CPU initialization, deciding whether VMX and SGX remain exposed to the kernel after BIOS/TXT constraints are applied. With `CONFIG_X86_VMX_FEATURE_NAMES`, it also converts VMX capability MSRs into `cpuinfo_x86::vmx_capability` feature words and legacy `/proc/cpuinfo` synthetic feature bits.

Important APIs and flow: `nosgx` clears SGX early through the `nosgx` boot option. `init_ia32_feat_ctl()` reads `MSR_IA32_FEAT_CTL`, clears VMX/SGX if the MSR is unavailable, decides whether KVM and SGX support require enabling bits, locks the MSR if firmware left it unlocked, writes VMX outside/inside SMX and SGX/SGX_LC bits as appropriate, then updates CPU caps. `init_vmx_capabilities()` reads VMX control, EPT/VPID, VMFUNC, and tertiary control MSRs and derives aggregate APICV/flexpriority/EPT/VPID capability bits.

State and persistence: persistent state is the locked hardware MSR; once locked, later software cannot change feature enablement until reset. The code also mutates per-CPU capability state.

Dependencies and integration: called from Intel CPU initialization and depends on KVM, SGX, TXT/tboot, VMX MSR definitions, and CPU feature infrastructure.

Risks and test signals: ordering is critical because VMX/SGX users trust CPU caps. Regression signals include boot logs for BIOS-disabled VMX/SGX, `/proc/cpuinfo` VMX feature names, KVM load behavior, SGX driver/KVM availability, and boot tests with locked/unlocked firmware MSR values.
