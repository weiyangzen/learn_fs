# sources/distributed-fs/ceph-client/arch/microblaze/lib/umodsi3.S

Purpose: provides unsigned 32-bit modulo helper `__umodsi3`.

Important APIs and state: operands are r5 dividend and r6 divisor; remainder r3. Saves r29-r31.

Control flow: zero divisor/dividend returns 0. Equal operands return 0. If divisor exceeds dividend, returns dividend. Otherwise it performs unsigned shift/subtract division and keeps the remainder.

State and persistence: pure arithmetic.

Dependencies and integration: compiler `%` operations and modules use it when hardware support is absent.

Risks and test signals: special high-bit path manually masks sign bits for one case and should be covered. Test divisor larger/equal, high-bit operands, random unsigned modulo, and zero divisor behavior.
