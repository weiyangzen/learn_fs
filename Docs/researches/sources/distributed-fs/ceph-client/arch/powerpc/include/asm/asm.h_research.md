# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm.h

Purpose: compatibility include for generic architecture assembly helpers.

Important APIs/types/functions: includes `<asm/asm-compat.h>` and `<asm/extable.h>`, making register-size macros and exception-table helpers available through the traditional `asm.h` include path.

Control flow: no runtime logic.

State and persistence: no state.

Dependencies and integration points: included by low-level PowerPC assembly and C inline assembly sources that expect a central architecture asm header.

Risks: because it is a broad include shim, changing it can affect many assembly files indirectly. Missing `extable` inclusion would break exception fixup annotations.

Test signals: architecture build coverage for assembly files and inline exception-table users.
