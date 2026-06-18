<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/static_call.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/static_call.h

Purpose: implements x86 architecture support for static calls, which patch direct call/jump sites for low-overhead indirect-call replacement. Important macros/functions include static-call trampoline/site declarations, architecture patch constants, inline/static call transformations, and text patching integration.

Control flow: static call users compile call sites and trampolines; registration/update paths patch instruction bytes to point at the selected target or return path. State is text patch-site metadata and patched kernel code.

Dependencies include jump labels, objtool, text patching, alternatives, module loading, and instruction encoding for CALL/JMP/RET. Risks include patching wrong instruction lengths, module unload races, CFI/IBT interaction, and stale target pointers. Test signals include static_call selftests, tracepoint/perf users, module load/unload with static calls, objtool validation, and IBT/CFI builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/static_call.h -->
