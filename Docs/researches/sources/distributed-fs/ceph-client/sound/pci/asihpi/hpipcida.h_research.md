# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpipcida.h

## Purpose
This header is an initializer fragment for the AudioScience HPI PCI device table.

## Important APIs, Types, And Functions
It contributes `struct pci_device_id` entries for TI DSP6205 devices mapped to `HPI_6205` and TI PCI2040 devices mapped to `HPI_6000`, both with AudioScience subvendor matching and wildcard subdevice.

## Control Flow
There is no standalone control flow. `hpimsgx.c` includes the fragment inside a static PCI ID array and later scans it to select the hardware handler from `driver_data`.

## State, Persistence, And Dependencies
The table data is static and read-only after compilation. It depends on PCI vendor/device constants and HPI handler symbols being defined by included HPI internals.

## Integration Points
`hpi_lookup_entry_point_function()` uses these entries during `HPI_SUBSYS_CREATE_ADAPTER` to bind a probed PCI device to the correct HPI implementation.

## Risks
Because this is a raw initializer fragment, syntax and ordering depend on the includer. The comment requires grouping by HPI entry point; violating that could make maintenance harder. Missing device IDs mean probe can map PCI memory but fail adapter creation.

## Test Signals
PCI probe tests should verify supported AudioScience cards match the expected handler, unsupported cards fail cleanly, and wildcard subdevice matching does not bind unintended hardware.
