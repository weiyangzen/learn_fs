# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.h

## Purpose
`pcie.h` is the minimal internal PCIe bus header for `brcmfmac`. It exposes the public wrapper object that connects generic bus state to the private PCIe implementation.

## Important APIs, types, and functions
- `struct brcmf_pciedev` contains `struct brcmf_bus *bus` and `struct brcmf_pciedev_info *devinfo`.
- `struct brcmf_pciedev_info` is intentionally forward-declared by use only; its definition remains private in `pcie.c`.

## Control flow
The header has no executable control flow. `pcie.c` allocates `struct brcmf_pciedev`, fills its `bus` and `devinfo` fields during probe, stores it under `bus->bus_priv.pcie`, and later retrieve it from bus operations, reset, remove, and PM paths.

## State and persistence behavior
The struct is a persistent ownership bridge for the PCI device lifetime. It does not own resources by itself; it points to the generic `brcmf_bus` allocation and the PCIe-specific `devinfo` allocation. Teardown in `pcie.c` frees the wrapper and the pointed-to state.

## Dependencies and integration points
The type depends on declarations of `struct brcmf_bus` and `struct brcmf_pciedev_info` from surrounding driver headers/source. It is consumed by the bus-private union in `bus.h` and by PCIe bus operations in `pcie.c`.

## Risks and edge cases
Because the wrapper only contains raw pointers, correctness depends on probe/remove ordering and clearing `dev_set_drvdata()` after free. There is no local lifetime protection or reference counting in this header.

## Test signals
Compile coverage is the main signal. Runtime signals come from PCIe probe/remove/reset paths successfully dereferencing `bus->bus_priv.pcie` without NULL or use-after-free faults.
