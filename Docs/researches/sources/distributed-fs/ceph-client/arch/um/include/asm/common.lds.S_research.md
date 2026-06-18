# sources/distributed-fs/ceph-client/arch/um/include/asm/common.lds.S Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/common.lds.S -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/common.lds.S

### Purpose
`common.lds.S` contributes assembly/linker-script layout for UML. It controls section placement and linker-provided symbols for this source tree area.

### Important APIs, Types, And Functions
Important symbols/macros visible in the file include `RO_DATA(4096)`; `EXCEPTION_TABLE(0)`; `INIT_SETUP(0)`; `PERCPU_SECTION(32)`; `PROVIDE (etext = .);`; `PROVIDE (sdata = .);`; `PROVIDE (_unprotected_end = .);`. It depends on `asm-generic/vmlinux.lds.h`.

### Control Flow
The assembler or linker consumes the directives at build time; runtime code later relies on the emitted section ranges, alignment, and symbols.

### State, Persistence, And Dependencies
Runtime persistence is the final binary layout, not mutable C state. Build-time state is the generated object or linker script output. Dependencies include `asm-generic/vmlinux.lds.h`.

### Integration Points And Risks
Risks include alignment regressions, missing section ranges, symbol-name drift, or layout changes that break early boot, init/exit scanning, alternatives, or syscall stubs.

### Test Signals
Link UML, inspect generated symbols/sections, and boot configurations that use the affected init, exit, exception, or stub sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/common.lds.S -->
