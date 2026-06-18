<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/Makefile

## Purpose
Builds the INT3472 driver family.

## Important Build Rules
`intel_skl_int3472_discrete.o` links `discrete.o`, `discrete_quirks.o`, `clk_and_regulator.o`, and `led.o`. `intel_skl_int3472_tps68470.o` links `tps68470.o` and board data. `intel_skl_int3472_common.o` links `common.o`.

## Control Flow And State
Kbuild assembles three modules from the one Kconfig symbol. The common module exports namespaced helpers used by both implementation modules.

## Dependencies, Risks, And Test Signals
Risks include missing namespace imports or object split drift. Test by building as modules and verifying symbol resolution for `INTEL_INT3472` and `INTEL_INT3472_DISCRETE` exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/Makefile -->
