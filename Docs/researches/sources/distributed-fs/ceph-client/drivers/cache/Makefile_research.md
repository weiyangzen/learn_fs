# sources/distributed-fs/ceph-client/drivers/cache/Makefile

## Purpose
The Makefile maps cache-maintenance Kconfig symbols to their driver objects.

## Important APIs, Types, And Functions
It builds `ax45mp_cache.o`, `sifive_ccache.o`, `starfive_starlink_cache.o`, and `hisi_soc_hha.o` from the corresponding `CONFIG_*` symbols.

## Control Flow
Kbuild includes an object only when its symbol is enabled. `HISI_SOC_HHA` may be built as a module because the Kconfig symbol is tristate; the RISC-V cache controller entries are bool options in this tree.

## State And Persistence
There is no runtime state. The file affects the kernel image or module set produced by a build.

## Dependencies And Integration Points
The object names correspond directly to source files in `drivers/cache` and to symbols declared in `Kconfig`.

## Risks And Edge Cases
The main risks are stale object mappings after file renames, mismatched symbol names, or expecting modular builds for bool-only entries. Build coverage across configurations is the best guard.

## Test Signals
Run Kbuild with each relevant `CONFIG_*` enabled and disabled, including `CONFIG_HISI_SOC_HHA=m`, and verify expected objects or modules are produced.
