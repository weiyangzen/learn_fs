# sources/distributed-fs/ceph-client/arch/um/include/asm/cpufeature.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/cpufeature.h -->
## sources/distributed-fs/ceph-client/arch/um/include/asm/cpufeature.h

### Purpose
`cpufeature.h` is a UML header under `sources/distributed-fs/ceph-client/arch/um/include/asm`. It defines architecture, shared, or subsystem contracts used by the corresponding C files and generic Linux code.

### Important APIs, Types, And Functions
Important declarations, macros, or types include `test_bit(bit, (unsigned long *)((c)->x86_capability))`; `test_cpu_cap(c, bit)`; `x86_this_cpu_test_bit(bit, cpu_info.x86_capability))`; `static __always_inline bool _static_cpu_has(u16 bit)`; `extern void setup_clear_cpu_cap(unsigned int bit);`; `#define _ASM_UM_CPUFEATURE_H`; `#define X86_CAP_FMT "%s"`; `#define x86_cap_flag(flag) x86_cap_flags[flag]`; `#define test_cpu_cap(c, bit)						\`; `#define CHECK_BIT_IN_MASK_WORD(maskname, word, bit)	\`; `#define cpu_has(c, bit)							\`. The file has 141 lines and includes or relies on `asm/processor.h`, `asm/asm.h`, `linux/bitops.h`.

### Control Flow
Most behavior is inline or declarative. Compile-time conditionals select UML-specific versus generic behavior, and runtime control flow occurs in callers or in implementation files declared here.

### State, Persistence, And Dependencies
The header itself owns no storage unless it declares extern symbols. The persistent state it describes is held in task, mm, IRQ, memory-layout, host-fd, or build-generated structures depending on the includer. Dependencies include `asm/processor.h`, `asm/asm.h`, `linux/bitops.h`.

### Integration Points And Risks
Risks include ABI or prototype drift, generic-header assumptions that do not match UMLs host-process model, missing config guards, and macros with side effects or fixed-size limits. Integration is through common Linux headers and UML implementation files.

### Test Signals
Build with the relevant Kconfig combinations, compile all includers, and run the subsystem paths that consume the declared macros or types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/include/asm/cpufeature.h -->
