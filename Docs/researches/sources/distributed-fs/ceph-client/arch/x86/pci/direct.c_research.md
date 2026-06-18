# sources/distributed-fs/ceph-client/arch/x86/pci/direct.c

## Purpose
Implements x86 direct PCI configuration-space access through legacy type 1 and type 2 IO port mechanisms. It probes whether those mechanisms work and installs raw PCI ops for base and sometimes extended config access.

## Important APIs and functions
- `pci_direct_conf1` provides type-1 `read`/`write` callbacks using ports `0xCF8`/`0xCFC`.
- `pci_direct_conf2` provides type-2 callbacks using `0xCF8`, `0xCFA`, and `0xC000`-based device windows.
- `pci_sanity_check()` verifies a candidate raw op by scanning bus 0 for plausible host bridge/VGA/vendor IDs, unless checks are disabled or BIOS year is new enough.
- `pci_check_type1()` and `pci_check_type2()` test hardware behavior while interrupts are disabled.
- `pci_direct_init()` installs a forced type and optionally enables type-1 extended access when `PCI_HAS_IO_ECS` is set.
- `pci_direct_probe()` requests IO regions, probes type 1 then type 2, sets `raw_pci_ops`, and marks `port_cf9_safe`.

## Control flow
The normal probe path tries type 1 first if allowed by `pci_probe`, reserves `0xCF8-0xCFF`, validates CF8 behavior and sanity, and installs `pci_direct_conf1` on success. If type 1 fails, it releases resources and tries type 2 by reserving `0xCF8-0xCFB` plus `0xC000-0xCFFF`. Read/write callbacks validate segment/bus/devfn/register limits, take `pci_config_lock`, program address ports, perform size-specific IO, and release the lock.

## State and persistence
The file updates global `raw_pci_ops`, optionally `raw_pci_ext_ops`, and `port_cf9_safe`. IO port reservations persist after a successful probe. Config operations are serialized through the global raw spinlock.

## Dependencies and integration points
Depends on x86 IO port accessors, DMI BIOS year, global `pci_probe` flags from `common.c`, `pci_config_lock`, and PCI core raw ops. `ce4100.c` delegates fallback operations to `pci_direct_conf1`; `amd_bus.c` can enable type-1 extended config.

## Risks and edge cases
Direct IO config is legacy and platform-sensitive. Type 1 only supports segment 0 in this path and uses extended register bits up to 4095; type 2 is limited to the first 256 config bytes and devices below slot 16. Incorrect sanity results can hide PCI or use a broken mechanism. IO region reservation failures correctly block use.

## Test signals
Boot logs should state selected configuration type. Validate config reads/writes before and after MMCONFIG availability, forced `pci=conf1/conf2`, old BIOS sanity-check behavior, and graceful failure when IO regions are unavailable.
