# sources/distributed-fs/ceph-client/arch/xtensa/lib/modsi3.S

Purpose: Implements exported signed 32-bit modulo helper `__modsi3` and, when needed, a normalization lookup table.

Important APIs, types, and functions: `__modsi3`, hardware `rems` path, software shift-subtract remainder path, `do_abs`, `do_nsau`, `ill` plus `DIV0`, `__nsau_data` for no-NSA cores, and `EXPORT_SYMBOL`.

Control flow: Uses hardware remainder when present. Software path records dividend sign, operates on absolute magnitudes, handles divisor zero/one and special cases, subtracts shifted divisor until remainder is found, then reapplies dividend sign.

State and persistence: Register-only except optional read-only `__nsau_data`; divide-by-zero traps via illegal instruction marker.

Dependencies and integration: Compiler-emitted modulo operations, trap divide-by-zero detection, core feature macros, and shared `__nsau_data` conventions.

Risks: Remainder sign must follow C semantics; divisor zero marker coupling to traps; table must be present on cores without NSA.

Test signals: Signed modulo tests with negative dividend/divisor, divisor one/zero, small and large values, and no-DIV32/no-NSA builds.
