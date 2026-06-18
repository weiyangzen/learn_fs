## sources/distributed-fs/ceph-client/arch/mips/kvm/stats.c

Purpose: Provides optional COP0 access histogram strings and dumping for MIPS KVM debugging.

Important APIs, types, and functions: `kvm_cop0_str[]` maps COP0 register indices to human-readable names. `kvm_mips_dump_stats()` prints nonzero COP0 access counters when `CONFIG_KVM_MIPS_DEBUG_COP0_COUNTERS` is enabled.

Control flow: VCPU destruction calls the dump helper from `mips.c`. With debug counters disabled, the function compiles to a no-op body. With counters enabled, it iterates all COP0 register/select slots and logs nonzero counts.

State and persistence: Reads `vcpu->arch.cop0.stat[i][j]`; it does not mutate state. Output is kernel log text only.

Dependencies and integration points: Depends on `N_MIPS_COPROC_REGS`, `N_MIPS_COPROC_SEL`, and COP0 stat fields in the VCPU architecture structure. Controlled by Kconfig debug option.

Risks: Histogram strings must remain aligned with COP0 register indices. Enabling debug counters can increase overhead and produce shutdown log volume.

Test signals: VCPU teardown with debug counters enabled, accesses across multiple select values, and default no-op behavior when disabled.
