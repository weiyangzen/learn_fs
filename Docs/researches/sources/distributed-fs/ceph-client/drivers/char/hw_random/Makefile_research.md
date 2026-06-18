# sources/distributed-fs/ceph-client/drivers/char/hw_random/Makefile

## Purpose
This Makefile maps `CONFIG_HW_RANDOM*` symbols to the common hwrng core object and provider modules. It is the build integration point for all hardware RNG drivers in the directory.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_HW_RANDOM) += rng-core.o` with `rng-core-y := core.o` builds the common framework.
- Each provider symbol appends one module object, for example `intel-rng.o`, `amd-rng.o`, `cctrng.o`, `arm_smccc_trng.o`, and `jh7110-trng.o`.
- Composite modules include `n2-rng-y := n2-drv.o n2-asm.o` and Cavium PF/VF objects under `CONFIG_HW_RANDOM_CAVIUM`.

## Control Flow
Kbuild evaluates configured symbols and builds the listed objects either built-in or as modules according to their tristate values. Composite object variables determine which source files are linked into a module.

## State and Persistence Behavior
No runtime state exists. Build state is the selected object list and module composition produced from `.config`.

## Dependencies and Integration Points
The file must stay synchronized with `Kconfig` symbol names and source filenames. It integrates with kbuild module naming, provider `MODULE_*` metadata, and the `rng-core` exported registration APIs.

## Risks
Missing or stale object mappings produce selected-but-unbuilt drivers. Composite mappings can break module linkage if one component is renamed. Object names are also visible as module filenames, so changes can affect user module-loading expectations.

## Test Signals
Run `make M=drivers/char/hw_random` with targeted symbols as built-in and modules, plus `allmodconfig`. Check that every Kconfig provider in this subset has a matching `obj-*` line and that `n2-rng` links both the C driver and assembly helper.
