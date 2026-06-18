# sources/distributed-fs/ceph-client/lib/lshrdi3.c

Purpose: libgcc-style helper for 64-bit logical right shift on targets that need compiler runtime support.

Important APIs/types/functions: `__lshrdi3(long long u, word_type b)`.

Control flow: if shift count is zero, returns input. Otherwise it views the 64-bit value as two 32-bit words with `DWunion`. For shifts of 32 or more, high becomes zero and low is shifted from the old high word. For smaller shifts, high is shifted right and low combines its shifted value with carries from the old high word.

State/persistence: stateless pure computation.

Dependencies/integration: exported symbol used by compiler-generated code on architectures lacking native helper availability. Depends on `linux/libgcc.h` word/union definitions.

Risks: assumes 32-bit word halves as defined by `DWunion`. Shift counts outside expected compiler-generated range may have undefined or surprising behavior.

Test signals: compiler/runtime tests should compare `__lshrdi3()` against native unsigned 64-bit logical right shifts for boundary counts 0, 1, 31, 32, 33, and 63.
