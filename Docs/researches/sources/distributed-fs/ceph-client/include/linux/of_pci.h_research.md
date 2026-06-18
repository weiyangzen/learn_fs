<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_pci.h -->
# sources/distributed-fs/ceph-client/include/linux/of_pci.h

## Purpose
This header declares OF helpers for PCI device-node lookup, devfn decoding, OF probe-only policy, and PCI interrupt mapping.

## Important APIs, types, and functions
When OF and PCI are enabled, it exports `of_pci_find_child_device()`, `of_pci_get_devfn()`, and `of_pci_check_probe_only()`. When OF IRQ is enabled, it exports `of_irq_parse_and_map_pci()`. Disabled stubs return `NULL`, `-EINVAL`, no-op, or zero.

## Control flow
PCI host/driver code matches a child node to a PCI `devfn`, decodes DT `reg` into a devfn, honors firmware probe-only policy, and maps PCI slot/pin interrupt swizzles through OF IRQ parsing.

## State and persistence
No state is owned by the header. Probe-only policy and IRQ mappings affect PCI core runtime state.

## Dependencies and integration points
It depends on OF, PCI, OF IRQ, PCI device nodes, and architecture host-bridge code.

## Risks and test signals
Risks include devfn decoding errors, wrong child node association for multifunction devices, probe-only policy regressions, IRQ pin swizzle mistakes, and zero IRQ fallback masking failures. Test PCI DT child lookup, multifunction slots, `reg` parsing, probe-only firmware settings, PCI INTx mapping, and `!CONFIG_PCI`/`!CONFIG_OF_IRQ` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of_pci.h -->
