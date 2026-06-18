<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acrestyp.h -->
# sources/distributed-fs/ceph-client/include/acpi/acrestyp.h

## Purpose
`acrestyp.h` defines ACPICA's in-memory resource descriptor ABI for ACPI resource templates such as `_CRS`, `_PRS`, `_SRS`, `_AEI`, and PCI routing tables. It maps AML resource descriptors into typed C structures for IRQs, DMA, I/O, memory, address spaces, GPIO, serial buses, pin controls, clocks, vendor data, and routing entries.

## Important APIs, types, and functions
Important base types are `acpi_rs_length`, `acpi_rsdesc_size`, `struct acpi_resource`, `union acpi_resource_data`, `struct acpi_pci_routing_table`, and `ACPI_NEXT_RESOURCE()`. Descriptor structures cover small and large resources: IRQ, DMA, dependent-function markers, I/O/fixed I/O, fixed DMA, vendor and typed vendor data, memory24/32/fixed memory32, address16/32/64, extended address64, extended IRQ, generic register, GPIO, I2C/SPI/UART/CSI2 serial bus, pin function/config/group descriptors, and clock input. Constants encode resource type IDs, memory cache/write attributes, interrupt trigger/polarity/share/wake attributes, DMA width, address decode and producer/consumer roles, serial bus modes, UART settings, pin config values, and resource sizing.

## Control flow
This header has no implementation, but ACPICA resource conversion code uses these structures when turning AML byte streams into linked `struct acpi_resource` buffers. Callers walk a returned buffer by advancing with `ACPI_NEXT_RESOURCE()` until `ACPI_RESOURCE_TYPE_END_TAG`. Resource walkers in `acpixf.h` pass each descriptor to caller callbacks.

## State and persistence behavior
Resource buffers are transient caller-owned allocations returned from ACPICA APIs. Persistent resource definitions live in firmware AML. Pointer fields in variable-length descriptors reference data inside generated buffers or separately managed allocations depending on conversion code.

## Dependencies and integration points
It depends on ACPICA packing, flexible-array, UUID, alignment, and pointer-arithmetic helpers. Linux ACPI resource parsing, platform-device creation, GPIO/I2C/SPI/UART enumeration, pinctrl setup, PCI IRQ routing, and operation-region setup all consume these descriptors.

## Risks and test signals
Risks include structure packing/alignment drift from AML layout, incorrect `length` fields causing resource-walk overruns, variable-length pointer lifetime bugs, unsupported new resource type IDs, endian/width errors in address descriptors, malformed firmware with missing end tags, and ambiguity between similar pin/GPIO/serial fields. Test signals include parsing `_CRS` with every descriptor family, malformed resource templates, extended IRQ and PCI routing tables, serial bus descriptors for I2C/SPI/UART/CSI2, pin group descriptors, `ACPI_NEXT_RESOURCE()` bounds checks, and conversion to address64 resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acrestyp.h -->
