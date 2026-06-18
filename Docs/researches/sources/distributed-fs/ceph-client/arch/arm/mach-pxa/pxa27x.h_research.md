<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.h

Purpose: umbrella PXA27x header with SoC-specific register definitions.

Important definitions: includes PXA2xx registers, PXA27x MFP macros, IRQs, and defines `ARB_CNTRL` plus bus arbiter park/lock bit masks.

Control flow and integration: included by PXA27x board and SoC code that need pin definitions or arbiter register access.

State and persistence: no local state; `ARB_CNTRL` macro accesses persistent hardware register state.

Dependencies: includes `linux/suspend.h`, address map, registers, MFP, and IRQ headers.

Risks and test signals: direct arbiter bit usage must be SoC-specific. Compile and runtime tests for PXA27x-only users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x.h -->
