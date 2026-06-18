# sources/distributed-fs/ceph-client/drivers/ssb/Makefile

## Purpose
Build recipe for the monolithic `ssb.o` object, composing core bus code, host transport support, built-in SSB core drivers, and the optional b43 PCI bridge.

## Important APIs, Types, and Functions
No runtime APIs are defined. It maps Kconfig symbols to object files: core `main.o scan.o`; optional `embedded.o`, `sprom.o`, `pci.o`, `pcihost_wrapper.o`, `pcmcia.o`, `bridge_pcmcia_80211.o`, `sdio.o`, `host_soc.o`; built-ins `driver_chipcommon.o`, `driver_chipcommon_pmu.o`, optional sflash, MIPS, EXTIF, PCI core, GigE, GPIO, and b43 bridge.

## Control Flow
Kbuild appends objects into `ssb-y` based on `CONFIG_*`, then links `obj-$(CONFIG_SSB) += ssb.o`. This means most optional subdrivers are linked into the SSB module/built-in image rather than built as separate modules.

## State and Persistence
Build output state is generated object membership. Runtime state is unaffected except through which code is present.

## Dependencies and Integration Points
Must remain synchronized with Kconfig and with init/exit calls in `main.c`, which may call optional functions that are conditionally built or stubbed through headers.

## Risks
Missing object selection causes link failures or disabled runtime features. Including bridge drivers inside `ssb.o` means init errors are logged but often intentionally non-fatal in `main.c`.

## Test Signals
Run builds for `SSB=m`, `SSB=y`, PCI host, PCMCIA host, host SoC/MIPS, and GPIO configurations. Confirm generated `ssb.o` includes the expected object list.
