## `sources/distributed-fs/ceph-client/arch/x86/include/asm/alternative.h`

Purpose: declares and implements x86 alternatives infrastructure macros for runtime instruction patching based on CPU features, SMP state, retpoline/return/call-thunk mitigation sites, and assembly/C inline alternatives.

Important APIs and types: `struct alt_instr` describes original and replacement instruction offsets, feature/flags, and lengths. Public patching entry points include `alternative_instructions()`, `apply_alternatives()`, `apply_retpolines()`, `apply_returns()`, `apply_seal_endbr()`, `apply_fineibt()`, call thunk patchers, ITS helpers, SMP alternatives, and text reservation checks. Macros include `ALTERNATIVE`, `ALTERNATIVE_2/3`, `ALTERNATIVE_TERNARY`, `alternative()`, `alternative_input()`, `alternative_io()`, and `alternative_call()`.

Control flow: compile-time macros emit original instructions, `.altinstructions` metadata, and `.altinstr_replacement` code. Early boot or module load patching walks metadata and overwrites instruction sites according to CPU feature bits and flags such as `ALT_NOT` or `ALT_DIRECT_CALL`. SMP lock prefix sites can be patched for UP/SMP behavior.

State and persistence: patched kernel text persists for runtime. Metadata sections persist as needed for modules/SMP switching. `alternatives_patched` reports patch state.

Dependencies and integration points: objtool annotations, static CPU features, module loader, retpoline/return thunk/CFI/IBT mitigations, SMP lock patching, and assembly users.

Risks: instruction length mismatches, unsafe direct-call patching, missing memory clobbers, or incorrect metadata can corrupt executable text. This is security-sensitive because it underpins speculation mitigations and call thunks.

Test signals: boot alternatives patch logs, objtool validation, module load/unload with alternatives, CPU mitigation selftests, SMP hotplug, and disassembly checks of patched sites.
