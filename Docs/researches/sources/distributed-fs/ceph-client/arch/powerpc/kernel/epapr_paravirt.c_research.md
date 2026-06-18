<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/epapr_paravirt.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/epapr_paravirt.c

## Purpose
`epapr_paravirt.c` enables ePAPR paravirtualization by reading hypercall instructions from the flattened device tree, patching the assembly hypercall stubs, and optionally installing an ePAPR idle handler.

## Important APIs, Types, And Functions
Globals are `epapr_paravirt_enabled` and private `epapr_has_idle`. Key functions are `early_init_dt_scan_epapr()`, `epapr_paravirt_early_init()`, and postcore initcall `epapr_idle_init()`. It patches `epapr_hypercall_start` and, for supported builds, `epapr_ev_idle_start`.

## Control Flow
Early DT scanning looks for a node with `hcall-instructions`, validates the property length is a multiple of four bytes and at most four instructions, converts big-endian instruction words to `ppc_inst_t`, patches the hypercall and idle stubs, records `has-idle` when present, and marks paravirt enabled. Later, `epapr_idle_init()` installs `ppc_md.power_save = epapr_ev_idle` only when the idle property was present and the build supports that assembly path.

## State And Persistence
State is runtime-only: patched kernel text plus boolean feature flags. There is no persistent storage.

## Dependencies And Integration Points
It depends on flat OF scanning, instruction patching, ePAPR assembly symbols, `ppc_md` machine descriptor, cache/text patching helpers, and build-time 32-bit/Book3E-64 conditions.

## Risks
Invalid instruction length aborts the scan with an error return but leaves no hypercall support. Patching must happen early enough before callers use `epapr_hypercall_start`. Installing idle on unsupported builds is intentionally compiled out.

## Test Signals
Signals include DT-based patching visible in disassembly or behavior, `epapr_paravirt_enabled` true only with valid instructions, ePAPR hypercall success, idle hook installation when `has-idle` is present, and safe no-op behavior without the property.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/epapr_paravirt.c -->
