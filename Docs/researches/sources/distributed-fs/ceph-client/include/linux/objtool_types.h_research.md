
# sources/distributed-fs/ceph-client/include/linux/objtool_types.h

Purpose: defines the compact data structures and numeric constants shared by objtool annotations in C and assembly.

Important APIs/types/functions: `struct unwind_hint` stores instruction offset, stack pointer offset, stack register, hint type, and signal flag. `UNWIND_HINT_TYPE_*` constants classify undefined coverage, end-of-stack, call frames, full/partial pt_regs, function generation, and save/restore pseudo-hints. `ANNOTYPE_*` constants identify no-ENDBR, retpoline-safe, instrumentation begin/end, unret begin, ignore alternatives, intra-function call, reachable, and no-CFI annotations. `ANNOTYPE_DATA_SPECIAL` tags special annotation data.

Control flow: `objtool.h` macros encode these values into special sections. Objtool decodes them while walking instructions and validating unwind/control-flow metadata.

State and persistence: no runtime state is stored. The values are compile-time ABI between annotated kernel code and objtool.

Dependencies and integration points: depends on fixed-width Linux types for C builds and must also be parseable by assembly. It integrates annotation emitters, objtool, ORC unwinder metadata generation, and mitigation validators.

Risks and test signals: risks include changing numeric constants without updating objtool, structure layout mismatches between C and assembly emission, and missing hint types for new entry patterns. Test signals include objtool build coverage, section decoding tests, ORC unwind validation, and assembly/C annotation compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/objtool_types.h -->
