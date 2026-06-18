## sources/distributed-fs/ceph-client/arch/arm64/include/asm/alternative-macros.h

### Purpose
Defines C and assembly macros for ARM64 alternatives: runtime instruction patching based on CPU capabilities or callbacks.

### Important APIs, Types, And Functions
Key macros are `ARM64_CB_SHIFT`, `ARM64_CB_BIT`, `ALTINSTR_ENTRY`, `ALTINSTR_ENTRY_CB`, `ALTERNATIVE`, `ALTERNATIVE_CB`, `_ALTERNATIVE_CFG`, `alternative_insn`, `alternative_if`, `alternative_if_not`, `alternative_else`, `alternative_endif`, `alternative_else_nop_endif`, and `alternative_cb_end`. Inline helpers are `alternative_has_cap_likely()` and `alternative_has_cap_unlikely()`.

### Control Flow
Compile-time macros emit original instructions, replacement instructions in subsections, and metadata in `.altinstructions`. Early boot or module load code later scans entries and patches instructions when a CPU capability is present. The inline `alternative_has_cap_*` helpers use `asm goto` so hot paths become patched branch/nop sequences.

### State, Persistence, And Dependencies
No writable state in this header; it emits ELF sections consumed by alternative patching code. Dependencies include cpucap definitions, instruction definitions, VDSO bits, assembler macros, and stringify/types helpers.

### Integration Points
Used throughout ARM64 assembly and inline C for errata workarounds, feature selection, VDSO, KVM, timers, GIC, and security mitigations.

### Risks
Replacement and original instruction lengths must match unless a callback is used. Bad labels, branches into alternative sections, or overflowing capability encodings can break boot-time patching.

### Test Signals
Build with many CPU feature configs, boot on heterogeneous ARM64 systems, enable module alternatives, inspect `.altinstructions`, and run objdump checks for length-balanced replacements and VDSO builds.
