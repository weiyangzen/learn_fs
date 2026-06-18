<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_dma.h

## Purpose
`acpi_dma.h` declares ACPI-based DMA controller registration and slave-channel lookup helpers.

## Important APIs, types, and functions
`struct acpi_dma_spec` carries channel ID, slave request line, and controller device. `struct acpi_dma` represents a registered controller with list node, device, xlate callback, private data, and CSRT request-line range. `struct acpi_dma_filter_info` is used by simple translation. APIs include controller register/free, devm registration, channel requests by index/name, and `acpi_dma_simple_xlate()`. Disabled stubs return `-ENODEV`, `ERR_PTR(-ENODEV)`, or `NULL`.

## Control flow
DMA controllers register an ACPI translation callback. Slave devices request channels, ACPI resources are parsed into `acpi_dma_spec`, and the controller callback maps the spec to a `dma_chan`.

## State and persistence behavior
Controller registration creates global/listed DMA controller state. Requests return normal dmaengine channel state; the header itself stores no state.

## Dependencies and integration points
It integrates ACPI CSRT/resource parsing with the dmaengine subsystem, `struct device`, and optional devm lifetime management.

## Risks and test signals
Risks include wrong request-line range handling, leaking controller registrations, mismatched channel names/indexes, and callers failing to handle `ERR_PTR`. Test signals include ACPI DMA controller probe/remove, devm cleanup, channel lookup by index/name, and builds without `CONFIG_DMA_ACPI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_dma.h -->
