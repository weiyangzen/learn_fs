<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/msr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/msr.h

Purpose: supplies shared MSR read/write helpers usable by early boot/compressed code. Important APIs include low-level `rdmsr`/`wrmsr`-style inline helpers with split 32-bit halves or 64-bit values.

Control flow: early architecture code reads or writes model-specific registers before full kernel helpers are available. State is CPU MSR state. Dependencies include x86 `rdmsr`/`wrmsr` instruction semantics and caller-provided MSR numbers.

Risks: invalid MSR accesses can fault in fragile early contexts; write ordering and feature checks must be handled by callers. Test signals include early CPU feature setup, compressed boot, SEV/TDX early paths using MSRs, and fault-free boot on CPUs lacking optional MSRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shared/msr.h -->
