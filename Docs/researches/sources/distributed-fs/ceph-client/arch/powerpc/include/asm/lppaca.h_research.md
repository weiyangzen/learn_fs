# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/lppaca.h

Purpose: defines the PAPR logical partition per-processor area (VPA/lppaca) and SLB shadow structures shared between pSeries guests and the hypervisor.

Important APIs/types/functions: `struct lppaca` maps the 640-byte architected VPA with fields for descriptor, size, dynamic hardware IDs, VPHN counters, DTL controls, donated CPU hints, wait/yield/dispatch accounting, nested KVM L1/L2 timing counters, and DTL index. `lppaca_of(cpu)`, `LPPACA_OLD_SHARED_PROC`, `lppaca_shared_proc()`, `get_lppaca()`, and `struct slb_shadow` are key interfaces.

Control flow: pSeries setup registers the VPA with the hypervisor; runtime code reads shared-proc status, yield counts, dispatch trace logs, and SLB shadow data. `lppaca_shared_proc()` checks firmware split-partition support and a non-architected old-status bit.

State and persistence: lppaca memory is per-CPU, cacheline-aligned, hypervisor-shared runtime state. It persists while registered and is updated by both OS and hypervisor. SLB shadow buffers persist as hypervisor-maintained SLB save areas.

Dependencies and integration points: depends on Book3S, PACA, firmware feature checks, MMU SLB constants, and pSeries VPA registration hypercalls. KVM and PHYP both consume parts of this layout.

Risks: layout, size, alignment, endianness, and 4 KiB boundary constraints are ABI-sensitive. Pre-v4.14 KVM requires advertising 1 KiB despite the canonical 640-byte structure. The shared-proc test uses a non-architected field and may need replacement.

Test signals: boot pSeries under KVM and PHYP, verify VPA registration, DTL logging, shared/dedicated processor detection, VPHN changes, and SLB shadow restore across context switches.
