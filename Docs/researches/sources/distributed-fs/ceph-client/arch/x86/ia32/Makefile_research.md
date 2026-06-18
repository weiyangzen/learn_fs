## `sources/distributed-fs/ceph-client/arch/x86/ia32/Makefile`

Purpose: builds IA32 emulation support objects for x86, currently the audit syscall classification object when audit is enabled.

Important build rules: `audit-class-$(CONFIG_AUDIT) := audit.o` and `obj-$(CONFIG_IA32_EMULATION) += $(audit-class-y)` include `audit.o` only when both IA32 emulation and audit are enabled.

Control flow: build-time only.

State and persistence: no runtime state in the Makefile.

Dependencies and integration points: Kconfig symbols `CONFIG_IA32_EMULATION` and `CONFIG_AUDIT`, and `audit.c`.

Risks: incorrect gating could either omit IA32 audit classification or build audit code without audit support.

Test signals: build matrix for IA32 emulation with/without audit; compat syscall audit tests.
