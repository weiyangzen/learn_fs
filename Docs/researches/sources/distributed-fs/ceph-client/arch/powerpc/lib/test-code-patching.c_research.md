<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/test-code-patching.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/test-code-patching.c

## Purpose
This late-init self-test validates PowerPC text and data patching helpers, especially branch encoding/translation and multi-instruction patching across page boundaries.

## Important APIs, types, and functions
Entry point `test_code_patching` runs `test_branch_iform`, `test_branch_bform`, `test_create_function_call`, `test_translate_branch`, `test_prefixed_patching`, `test_multi_instruction_patching`, and `test_data_patching`. It exercises `create_branch`, `create_cond_branch`, `translate_branch`, `patch_instruction`, `patch_instruction_site`, `patch_instructions`, `patch_uint`, `patch_ulong`, and `ppc_inst_*` helpers.

## Control flow
Each test builds temporary instruction buffers, writes branch or prefixed opcodes, patches code/data, then uses `check()` to emit a line-numbered error on mismatch. Range-limit tests intentionally expect errors for out-of-range or unaligned branch targets. The multi-instruction test allocates pages with `vzalloc` and checks repeated and memcpy patch modes within and across pages.

## State and persistence behavior
The self-test mutates a trampoline function, temporary vmalloc buffers, and stack arrays, then frees vmalloc allocations. It logs failures but does not persist state or abort boot.

## Dependencies and integration points
It integrates with `asm/text-patching.h`, PowerPC instruction wrappers, vmalloc, late initcalls, and prefixed instruction support on PPC64.

## Risks and edge cases
Important edge cases are branch reach limits, absolute versus relative addressing, link-bit preservation, condition flag masking, prefixed 64-bit instruction layout, page-crossing patch writes, and alignment requirements for `patch_ulong`.

## Test signals
Primary signal is absence of `code-patching: test failed at line ...` after the late initcall logs that self-tests are running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/test-code-patching.c -->
