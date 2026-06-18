## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/srem_mod.S

### Purpose
`srem_mod.S` implements floating-point `FMOD` and IEEE `FREM` for finite nonzero operands. It computes the remainder of `X` divided by `Y`, returning the correct sign, quotient bits, and remainder value according to the selected operation.

### Important APIs, Types, And Functions
Exports are `smod` and `srem`, which share the `Mod_Rem` body. Scratch aliases define `Mod_Flag`, `SignY`, `SignX`, `SignQ`, `Sc_Flag`, `Y`, and `R`. The only external dependency is `t_avoid_unsupp`, used at finish to avoid denormal unsupported traps during result handling. A `Scale` constant supports denormal scaling.

### Control Flow
The common path saves operand signs, strips signs, records MOD versus REM, normalizes denormal operands if needed, and compares exponents. It initializes a scaled remainder `R`, quotient accumulator `Q`, and loop count from exponent difference. `Mod_Loop` repeatedly compares/subtracts `Y`, shifts `R`, and accumulates quotient bits. After the loop, MOD returns the signed remainder directly, while REM compares `R` with `Y/2`, possibly performs a final subtract, and handles the exact tie case by checking quotient parity. Finish restores signs, quotient bits, and branches through `t_avoid_unsupp`.

### State, Persistence, And Dependencies
All state is held in FPSP scratch slots and data registers. The routine writes the result operand and FPSR quotient byte but keeps no persistent state. It assumes NaNs, infinities, and zero divisors were handled before entry, as stated in the file comments.

### Integration Points
The arithmetic function dispatcher calls `smod` or `srem` for FMOD/FREM normal finite cases. The result then flows through common FPSP storage and exception machinery, with `t_avoid_unsupp` guarding denormal replay behavior.

### Risks
Remainder semantics are branch-sensitive. FMOD and FREM differ at the post-loop step, especially when `R` is exactly `Y/2`, where IEEE remainder chooses the even quotient. Quotient sign and low seven quotient bits must be correct for FPSR. Denormal scaling must not change the mathematical remainder or lose sign information.

### Test Signals
Test positive and negative X/Y combinations, exact multiples, `R < Y/2`, `R > Y/2`, exact half-way ties with even and odd quotients, large exponent differences, denormal operands, and quotient byte/sign behavior. Compare FMOD versus FREM against an m68k/68881 reference or high-precision software model.
