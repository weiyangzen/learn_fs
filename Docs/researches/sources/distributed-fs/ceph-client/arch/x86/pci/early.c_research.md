# sources/distributed-fs/ceph-client/arch/x86/pci/early.c

## Purpose
Provides minimal early-boot direct PCI config access helpers using type-1 CF8/CFC IO ports before the full PCI subsystem and locking/probing infrastructure are available.

## Important APIs and functions
- `read_pci_config()`, `read_pci_config_byte()`, and `read_pci_config_16()` read 32/8/16-bit config values.
- `write_pci_config()`, `write_pci_config_byte()`, and `write_pci_config_16()` write 32/8/16-bit config values.
- `early_pci_allowed()` reports whether early type-1 access is allowed by `pci_probe` flags.

## Control flow
Each read/write composes a type-1 config address from bus, slot, function, and offset, writes it to `0xcf8`, then performs the requested IO operation at `0xcfc` plus byte/word offset. `early_pci_allowed()` requires `PCI_PROBE_CONF1` and absence of `PCI_PROBE_NOEARLY`.

## State and persistence
No state is stored locally. The functions directly touch hardware IO ports and observe global `pci_probe` policy.

## Dependencies and integration points
Depends on x86 IO accessors and `pci_probe` from `common.c`. Used by early native bridge probes such as `amd_bus.c` and `broadcom_bus.c`, and by AMD ECS enabling before normal PCI enumeration is fully established.

## Risks and edge cases
There is no locking in these early helpers, so callers must use them only during safe early boot phases. They assume type-1 config access and segment 0. Incorrect use after `pci=noearly` or on systems without CF8/CFC support can produce invalid hardware accesses.

## Test signals
Early bridge resource probes should disappear when `pci=noearly` is used and should work on systems where type-1 access is valid. Failures surface as missing hardware-probed root resources or inability to enable AMD ECS early.
