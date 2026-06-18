# sources/distributed-fs/ceph-client/include/asm-generic/unwind_user.h

Purpose: empty generic placeholder for architecture user unwinding support.

Important APIs/types/functions: none; it only provides include guards.

Control flow: none.

State and persistence: none.

Dependencies and integration points: included by generic or architecture code that wants a stable `<asm/unwind_user.h>` include path even when no architecture-specific user unwinder exists.

Risks: consumers must not assume unwind operations are available from this generic header. Architecture ports needing user stack unwinding must override it.

Test signals: build-only coverage that includes this header on architectures without a custom implementation.
