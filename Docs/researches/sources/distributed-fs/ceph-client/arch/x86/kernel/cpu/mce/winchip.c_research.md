# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/winchip.c

Purpose: supports IDT WinChip C6 machine-check reporting for ancient x86 configurations.

Important APIs and flow: `winchip_machine_check()` prints an emergency machine-check message and taints the kernel. `winchip_mcheck_init()` reads `MSR_IDT_FCR1`, enables EIERRINT and MCE reporting bits, writes the MSR back, sets CR4.MCE, and logs enablement for CPU0.

State and persistence: state is hardware MSR configuration, CR4.MCE, and `mce_flags.winchip` set by common core. No queued records or persistent storage.

Dependencies and integration: selected by ancient MCE support and invoked from common CPU init/exception redirection for Centaur family 5.

Risks and test signals: minimal modern coverage and hardware scarcity. Signals are build coverage with `CONFIG_X86_ANCIENT_MCE`, boot on supported WinChip hardware or emulator, and int18 emergency log behavior.
