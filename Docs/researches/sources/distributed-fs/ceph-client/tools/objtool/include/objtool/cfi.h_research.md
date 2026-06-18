# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/cfi.h

Purpose: architecture-neutral CFI data model used by objtool stack validation and ORC generation.

Important APIs/types/functions: defines sentinel bases `CFI_UNDEFINED`, `CFI_CFA`, `CFI_SP_INDIRECT`, `CFI_BP_INDIRECT`; `struct cfi_reg`; `struct cfi_init_state`; and `struct cfi_state` with register rules, value tracking, CFA, stack size, DRAP metadata, hint type, scratch flags, signal/end/force flags, and hash node.

Control flow: none; it provides the state structure transformed by validation code.

State and persistence behavior: `struct cfi_state` instances are hashed and shared during validation. Their contents are later serialized into ORC entries by architecture ORC code.

Dependencies and integration points: includes architecture register constants from `arch/cfi_regs.h` and Linux list/hash support. Used by `check.c`, architecture decoders, ORC writers, and unwind hint readers.

Risks: `hash` must remain first for `cficmp()` assumptions in `check.c`. Any field added to `struct cfi_state` changes hash/equality behavior and can affect CFI reuse/conflict detection.

Test signals: stack validation tests should exercise CFA base changes, saved/restored registers, indirect stack bases, DRAP, forced undefined hints, signal frames, and alternative CFI conflict detection.
