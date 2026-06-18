<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/olpc.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/olpc.c

## Purpose
`olpc.c` implements PCI config-space simulation for OLPC XO-1 systems using AMD Geode GX/LX plus CS5536 devices when VSA firmware emulation is not used. It replaces SMM-based PCI virtualization with kernel-side table-backed config headers for integrated devices.

## Important APIs, types, and functions
Static header tables describe simulated northbridge, framebuffer, AES, ISA, AC97, OHCI, and EHCI config spaces for GX/LX variants. `is_simulated()` selects bus-0 Geode slots, `hdr_addr()` handles normal reads versus BAR-size probing, `pci_olpc_read()` and `pci_olpc_write()` implement raw config ops, and `pci_olpc_init()` installs `raw_pci_ops`.

## Control flow
Non-simulated devices fall back to `pci_direct_conf1`. Simulated reads choose a table by devfn, return zero beyond stored config range, or all ones for absent devices. BAR writes of `~0` set `bar_probing`, causing the next read to return the corresponding size mask instead of normal header data. Other writes are ignored except for warnings on unexpected registers.

## State and persistence behavior
File-local state includes `ff_loc`, `zero_loc`, `bar_probing`, and `is_lx`. The simulation is mostly read-only; it does not persist writes into the tables. `bar_probing` is a single global one-shot flag and assumes PCI core sizing reads immediately follow writes.

## Dependencies and integration points
It depends on Geode/OLPC platform detection, type-1 direct PCI access for external devices, and the PCI core's standard BAR sizing sequence. It avoids the external VSA SMM path for suspend/resume speed and maintainability.

## Risks and edge cases
The global BAR-probing flag is not device-specific, so unexpected concurrent config accesses could read a size mask for the wrong simulated device. Ignoring config writes is acceptable only because these integrated devices expose mostly fixed resources. Header tables must accurately match LX versus GX hardware.

## Test signals
Boot XO-1 with VSA disabled, enumerate simulated Geode devices, verify BAR sizes/resources, USB/audio/framebuffer availability, suspend/resume speed, and absence of unexpected config-write warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/olpc.c -->
