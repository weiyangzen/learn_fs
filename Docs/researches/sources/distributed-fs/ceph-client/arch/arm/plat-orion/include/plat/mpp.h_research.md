# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/mpp.h

Purpose: Defines generic Marvell Orion MPP pin-configuration encoding and declares the configuration routine.

Important APIs/macros: `MPP_NUM(x)` extracts pin number, `MPP_SEL(x)` extracts mux select value, and `GENERIC_MPP(_num, _sel, _in, _out)` encodes pin, mux, and GPIO input/output capability bits. `MPP_INPUT_MASK` and `MPP_OUTPUT_MASK` are capability masks. `orion_mpp_conf()` applies a zero-terminated MPP list to hardware.

Control flow/state: Board-specific macros typically extend `GENERIC_MPP` with variant bits. `orion_mpp_conf()` uses this encoding to update mux registers and call GPIO validity setup. No state is stored in the header.

Dependencies/integration: Integrates machine pinmux tables with `mpp.c` and `gpio.c`. Correct variant masks prevent applying mux selections unavailable on a given SoC.

Risks/tests: Misencoded MPP entries can disable peripheral pins or mark invalid GPIO directions as valid. Tests should validate each board's MPP table against hardware variant masks and confirm resulting GPIO input/output permissions.
