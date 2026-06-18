# sources/distributed-fs/ceph-client/arch/sparc/lib/GENcopy_from_user.S

Purpose: Generic SPARC64 raw copy-from-user implementation wrapper. It parameterizes `GENmemcpy.S` so loads come from user address space through `ASI_AIUS` and the generated function is `GENcopy_from_user`.

Important APIs/functions: Defines `EX_LD`, `LOAD(type,addr,dest)`, `EX_RETVAL(x)`, `PREAMBLE`, and `FUNC_NAME`. The included body emits `GENcopy_from_user(dst, src, len)`.

Control flow: On kernel builds the preamble reads `%asi`; if the current address-space identifier is not `ASI_AIUS`, it branches to `raw_copy_in_user`. Otherwise the generic byte/word/xword copy loops in `GENmemcpy.S` run with exception-table guarded user loads.

State and persistence: No persistent state. It temporarily relies on `%asi`, integer registers, and exception-table metadata.

Dependencies/integration: Depends on `GENmemcpy.S`, `raw_copy_in_user`, SPARC alternate address spaces, and the kernel exception-table fixup mechanism. It is selected by generic CPU patching and built for `CONFIG_SPARC64`.

Risks/test signals: Highest risks are wrong residual count on a user fault, `%asi` mismatch handling, and bad branch/fixup targets. Test with fault-injection user copies, kernel/user address-limit transitions, zero/small/unaligned/large lengths, and SPARC64 boot smoke tests that exercise patched copy routines.
