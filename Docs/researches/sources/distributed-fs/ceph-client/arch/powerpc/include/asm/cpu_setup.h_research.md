## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpu_setup.h

Purpose: declares CPU-family setup and restore entry points used by the CPU table and low-level bring-up code.

Important APIs/types/functions: setup functions include POWER7 through POWER10, e500 variants, 440/460/APM821xx, 603/604/750/7400/745x, PPC970, PA6T, e5500, and e6500. Restore functions exist for POWER7 through POWER10, PA6T, PPC970, e5500, and e6500.

Control flow: implemented in architecture code and referenced through `struct cpu_spec` setup/restore callbacks. Boot CPU setup initializes CPU-specific registers; secondary CPU and resume paths call restore variants.

State and persistence: the functions program CPU SPRs, cache/BHT/errata workarounds, and similar processor state outside this header.

Dependencies and integration: tightly coupled to `struct cpu_spec` declarations in `cputable.h`, early assembly bring-up, CPU hotplug, and suspend/resume.

Risks and test signals: declarations must match assembly/C implementations and CPU table entries. Missing restore support causes secondary CPU or resume misconfiguration. Test signals include per-family boot, SMP bring-up, CPU hotplug, suspend/resume, and build coverage for all configured CPU families.
