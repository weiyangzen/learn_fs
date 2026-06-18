# sources/distributed-fs/ceph-client/arch/powerpc/lib/div64.S

This 32-bit PowerPC helper implements `__div64_32`, dividing an unsigned 64-bit dividend by a 32-bit divisor. The caller passes a pointer to the 64-bit dividend in `r3` and the divisor in `r4`; the routine overwrites the pointed dividend with the 64-bit quotient and returns the 32-bit remainder in `r3`. It assumes the high 32 bits of the dividend are initially nonzero.

Control flow first handles the case where the high word can produce a high quotient word directly. It then loops while the high word remains nonzero, estimating a quotient component by normalizing the dividend/divisor when the high bits permit, multiplying the estimate by the divisor, subtracting the product from the 64-bit working dividend with carry/borrow, and accumulating the low quotient word. When the high word is zero, it performs a final 32-bit `divwu` for the low word and stores both quotient words.

State is only the in-place dividend/quotient memory and registers. Dependencies include the 32-bit PowerPC integer instruction set and the kernel's generic div64 helper ABI. Risks are divide-by-zero being the caller's responsibility, quotient estimate edge cases, and carry/borrow correctness. Test signals include generic `do_div` users, arithmetic selftests on 32-bit PowerPC, and boundary values where high dividend is near or above divisor.
