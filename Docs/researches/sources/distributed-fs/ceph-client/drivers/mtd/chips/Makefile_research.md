# sources/distributed-fs/ceph-client/drivers/mtd/chips/Makefile

## Purpose

This `Makefile` maps MTD chip-driver Kconfig symbols to probe, utility, command-set, and simple map-backed chip driver objects.

## Important Build Targets

`chipreg.o` is built whenever `CONFIG_MTD` is enabled. CFI and JEDEC support build `cfi_probe.o`, `jedec_probe.o`, `gen_probe.o`, and `cfi_util.o` according to the selected symbols. Command-set implementations map directly to `cfi_cmdset_0020.o`, `cfi_cmdset_0002.o`, and `cfi_cmdset_0001.o`. Simple map drivers are `map_ram.o`, `map_rom.o`, and `map_absent.o`.

## Control Flow

Kbuild descends here from `drivers/mtd/Makefile`. Each `obj-$(CONFIG_...)` line is resolved from `.config`. Probe support and command-set support can be built independently enough that a probe can identify devices while command-set modules provide the operation callbacks for matching IDs.

## State and Persistence Behavior

The file has no runtime state, but it controls whether the kernel image or module tree contains the chip registry, CFI/JEDEC probing, command-set drivers, and simple RAM/ROM/absent devices. Missing objects translate directly into unsupported flash at runtime.

## Dependencies and Integration Points

This file is paired with `drivers/mtd/chips/Kconfig`. `cfi_cmdset_0001.o` and `cfi_cmdset_0002.o` export command-set entry points consumed by generic CFI probe code. `chipreg.o` supports chip-driver registration. `cfi_util.o` provides shared helpers used by the command-set drivers.

## Risks and Edge Cases

Symbol/object mismatch is the main risk. For example, enabling `MTD_CFI_AMDSTD` must build `cfi_cmdset_0002.o`; otherwise AMD/Fujitsu CFI flash probes would identify devices but lack operation methods. Conversely, building probe utilities without command-set support may detect but not use some chips.

## Test Signals

Build tests should assert that each chip Kconfig symbol produces the expected object or module. Runtime smoke tests should verify CFI probe plus command-set binding for Intel/Sharp and AMD/Fujitsu flash, and simple map RAM/ROM registration when those symbols are selected.
