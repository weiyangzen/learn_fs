<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/rsparser.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/rsparser.c

Purpose: Translate ACPI `_CRS` and `_PRS` resource descriptors to PnP resource lists/options, and encode PnP resources back into ACPI templates for `_SRS`.

Important APIs/types/functions: `pnpacpi_allocated_resource()` handles current resources; option parsers handle DMA, IRQ, extended IRQ, IO/fixed IO, memory24/32/fixed, address descriptors, and dependent functions. `pnpacpi_build_resource_template()` creates a type-preserving template from `_CRS`; `pnpacpi_encode_resources()` fills it using current PnP resources. Helper `decode_irq_flags()` maps Linux IRQ flags to ACPI triggering/polarity/shareability.

Control flow: current-resource parsing clears resources then walks `_CRS`. It adds address-space resources, interrupts (including GPIO interrupt resources), memory, IO, DMA, and selected vendor resources. Option parsing walks `_PRS`, creating dependent sets and possible resource options. Encoding counts supported `_CRS` descriptors, allocates a resource array plus end tag, copies descriptor types, then encodes resources in descriptor order by resource type counters.

State/persistence: current PnP resource list and possible option list are rebuilt from ACPI firmware. Encoding produces a temporary ACPI buffer consumed by `acpi_set_current_resources()`.

Dependencies/integration: ACPI resource helpers, PCI IRQ penalization, PnP resource registration, ACPI GPIO IRQ helpers, and HP CCSR vendor UUID handling.

Risks: multi-interrupt `_CRS` descriptors cannot be re-encoded; code disables `PNP_WRITE` in that case. Address option parsing simplifies ranges to fixed minimum/length resources. Unsupported serial bus/generic register resources are ignored or unencodable. Descriptor order and resource counters must match `_CRS` shape, or `_SRS` receives wrong values.

Test signals: ACPI devices with every supported descriptor type, GPIO interrupt resources, HP vendor CCSR, multiple IRQ descriptors, `_PRS` dependent sets, `_SRS` round-trip, and invalid IRQ/DMA flag values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/rsparser.c -->
