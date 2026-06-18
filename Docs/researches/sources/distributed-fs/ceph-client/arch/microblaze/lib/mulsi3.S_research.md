# sources/distributed-fs/ceph-client/arch/microblaze/lib/mulsi3.S

Purpose: provides signed 32-bit multiply helper `__mulsi3` for cores/builds without hardware multiply.

Important APIs and state: operands are r5/r6, result r3. The routine uses shift/add multiplication and sign correction.

Control flow: zero operands return 0. Negative operands are made positive while saving result sign; loop shifts the multiplier and conditionally accumulates multiplicand; negative result is negated before return.

State and persistence: pure arithmetic.

Dependencies and integration: exported to modules and used by compiler-generated multiplication when needed.

Risks and test signals: overflow follows low 32-bit two's-complement behavior. Test sign combinations, zero, one, high-bit operands, and no-hardware-mul builds.
