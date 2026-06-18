
# sources/distributed-fs/ceph-client/include/linux/objtool.h

Purpose: provides C and assembly annotation macros consumed by objtool for unwind hinting, stack-frame validation exceptions, reachable-code marking, and mitigation validation markers.

Important APIs/types/functions: when `CONFIG_OBJTOOL` is enabled, `UNWIND_HINT()` emits records into `.discard.unwind_hints`; `STACK_FRAME_NON_STANDARD()` and `STACK_FRAME_NON_STANDARD_FP()` mark functions exempt from stack-frame validation; `ASM_REACHABLE` emits `.discard.reachable`; assembly variants define equivalent macros. Disabled builds make these annotations empty. `VALIDATE_UNRET_BEGIN` maps to `ANNOTATE_UNRET_BEGIN` only for configured noinstr validation and unret/SRSO mitigation combinations.

Control flow: low-level C inline asm or assembly entry code places hints at control-flow points. Objtool reads discard sections during build analysis, validates stack/unwind state, and generates ORC metadata or suppresses warnings for marked non-standard functions.

State and persistence: annotations are build-time metadata in special ELF sections, discarded or consumed during tooling. They affect generated unwind metadata, not runtime mutable state.

Dependencies and integration points: depends on `objtool_types.h`, annotation macros, config options for objtool/frame pointers/noinstr validation, and assembly preprocessing. It integrates architecture entry code, ORC unwinder generation, retpoline/unret validation, and kernel build checks.

Risks and test signals: risks include overusing non-standard frame exemptions, incorrect unwind hints causing bad stack traces, missing assembly annotations for entry/interrupt code, and config-dependent annotation drift. Test signals include objtool warning-free builds, ORC unwind selftests, frame-pointer builds, noinstr validation with mitigations enabled, and runtime stack traces through annotated assembly paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/objtool.h -->
