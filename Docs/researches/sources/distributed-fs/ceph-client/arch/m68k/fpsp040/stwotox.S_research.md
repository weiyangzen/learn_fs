# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/stwotox.S

Purpose: implements FPSP exponential base routines for `ftwotox` (`2**X`) and `ftentox` (`10**X`), including denormal entries. Results are returned in `%fp0` with common FPSP exception exits handling overflow, underflow, and inexact behavior.

Important APIs/types/functions: exported labels are `stwotox`, `stwotoxd`, `stentox`, and `stentoxd`. It defines range constants `BOUNDS1`/`BOUNDS2`, log conversion constants, polynomial coefficients `EXPA1..EXPA5`, `HUGE`, `TINY`, and a 64-entry `EXPTBL` table storing split approximations to `2^(j/64)`.

Control flow: denormal entries return `1+X`. `stwotox` bounds-checks `|X|`, computes `N=round(64X)`, splits `N` into `64(M+M')+J`, fetches `2^(J/64)` from `EXPTBL`, computes reduced `R=(X-N/64)*log(2)`, and jumps to `expr`. `stentox` similarly computes `N=round(X*64*log2(10))`, uses split `log10(2)/64` to reduce, multiplies by `log(10)`, then shares `expr`. `expr` evaluates `exp(R)-1` and reconstructs the scaled result using `FACT1`, `FACT2`, and `ADJFACT`. Large positive inputs branch to `t_ovfl`; large negative inputs branch to `t_unfl`; tiny inputs return `1+X`.

State and persistence: no persistent state. Scratch aliases `N`, `X`, `ADJFACT`, `FACT1`, and `FACT2` hold decomposition state and scaled table values. `%d1` is restored to FPCR immediately before the final multiply that should expose user rounding/exceptions.

Dependencies/integration: depends on `fpsp.h` and common exits `t_unfl`, `t_ovfl`, and `t_frcinx`. `tbldo.S` dispatches `ftwotox` and `ftentox` source classes here. The routines share mathematical structure with other FPSP exponential helpers.

Risks: reconstruction is sensitive to off-by-one errors in `N` splitting, table displacement `J*16`, and exponent adjustments in `FACT1/FACT2/ADJFACT`. The code directly clears the input sign byte before underflow/overflow exits because those handlers expect positive magnitude, so sign handling must be kept in sync with common exception code.

Test signals: cover denormal and tiny inputs, base-2 and base-10 normal ranges, exact integer exponents, threshold values near `16480` and `16480*log2/log10`, large positive overflow, large negative underflow, all rounding modes, and ULP checks across table bucket boundaries.
