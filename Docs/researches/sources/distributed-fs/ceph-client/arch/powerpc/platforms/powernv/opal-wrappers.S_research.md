## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-wrappers.S

### Purpose
`opal-wrappers.S` implements the low-level PowerPC transition into OPAL firmware and restoration back to Linux, including MSR and endian handling.

### Important APIs, Types, And Functions
The file defines `_GLOBAL_TOC(__opal_call)`, which receives OPAL arguments in `r3-r10`, the OPAL opcode in stack parameter `R11`, and the saved MSR in stack parameter `R12`.

### Control Flow
The wrapper saves LR, derives an OPAL MSR by clearing IR, DR, and LE bits, loads the OPAL base/entry pair from the global `opal` structure, sets HSRR0/HSRR1 for the firmware entry, loads the opcode into `r0`, and enters OPAL with `hrfid`. On return it restores the caller MSR. Big-endian builds use `mtmsrd`; little-endian builds use encoded instructions to byte-reverse the saved MSR and return through HSRR so endian state can switch correctly. The wrapper then restores the TOC and LR and returns.

### State, Persistence, And Dependencies
The wrapper consumes the global `opal` descriptor initialized from device tree by `opal.c`. It mutates privileged processor state only for the duration of the firmware call. Dependencies include PowerPC SPRs, HSRR return semantics, stack layout constants, TOC conventions, and endian-specific instruction encodings.

### Integration Points
Generated OPAL C wrappers and exported OPAL symbols eventually call this routine to enter firmware. It is also the natural place for OPAL tracing hooks in the wider build.

### Risks
Any stack parameter offset, MSR mask, TOC restore, or endian transition error would corrupt kernel execution after firmware return. Little-endian restoration relies on raw encoded instructions, making assembler/disassembler review important. Firmware calls run with translation disabled according to the prepared MSR.

### Test Signals
Validation should include big- and little-endian boots, simple OPAL token calls, failing/invalid calls, trace-enabled builds, nested call avoidance at higher layers, and stress around interrupts/preemption disabled by callers.
