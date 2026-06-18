# sources/distributed-fs/ceph-client/drivers/char/hw_random/n2-asm.S

## Purpose
This SPARC64 assembly file provides low-level Niagara2 RNG hypervisor call wrappers used by the `n2-rng` driver. It invokes fast traps for diagnostic control, control register reads/writes, and random data reads.

## Important APIs, Types, and Functions
- Exported entry points include `sun4v_rng_get_diag_ctl`, `sun4v_rng_ctl_read_v1`, `sun4v_rng_ctl_read_v2`, `sun4v_rng_ctl_write_v1`, `sun4v_rng_ctl_write_v2`, `sun4v_rng_data_read_diag_v1`, `sun4v_rng_data_read_diag_v2`, and `sun4v_rng_data_read`.
- Hypervisor opcodes come from `asm/hypervisor.h`, such as `HV_FAST_RNG_CTL_READ` and `HV_FAST_RNG_DATA_READ`.
- Linkage macros `ENTRY` and `ENDPROC` provide callable kernel symbols.

## Control Flow
Each wrapper places the proper hypervisor function number in `%o5`, arranges argument or output-pointer registers for ABI version differences, executes `ta HV_FAST_TRAP`, stores returned output registers to caller-provided addresses when needed, and returns the hypervisor status in the return register.

## State and Persistence Behavior
The assembly maintains no state. Any persistent state is in the hypervisor RNG facility and in memory locations supplied by the C caller for returned values.

## Dependencies and Integration Points
It depends on SPARC64 Sun4v hypervisor ABI, `n2rng.h`, Linux linkage macros, and the composite `n2-rng` module built by the Makefile.

## Risks
Register calling convention mismatches would corrupt outputs or return status. Version-specific wrappers store different numbers of return registers, so the C driver must call the correct symbol for the negotiated hypervisor RNG API.

## Test Signals
Build on SPARC64, verify symbols link with `n2-drv.o`, test hypervisor API v1/v2 paths, validate returned status propagation, and exercise diagnostic/data reads under a Sun4v environment.
