<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/rsparser.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/rsparser.c

Purpose: Parser and encoder for PnP BIOS resource data streams. It converts allocated resources, possible resource options, compatible IDs, and names between packed firmware tags and PnP core structures.

Important APIs/types/functions: tag constants for small/large PnP BIOS resources. Allocated parsers handle IO, memory, IRQ, DMA, memory32, and fixed memory/IO. Option parsers register possible resources and dependent sets. Compatible ID parser adds PnP IDs and names. Encoding helpers write current PnP resources back into allocated-resource tags. Public functions are `pnpbios_parse_data_stream()`, `pnpbios_read_resources_from_node()`, and `pnpbios_write_resources_to_node()`.

Control flow: full parse starts at `node->data`, parses allocated resources until first end tag, parses resource options until second end tag, then parses compatible IDs/names until final end tag. Read-only current-resource parse stops after allocated resources. Write path walks allocated-resource tags and overwrites base/length/bitmask fields using resource counters for IO/IRQ/DMA/MEM.

State/persistence: mutates `dev->resources`, `dev->options`, ID list, and device name. Encoding mutates the in-memory BIOS node buffer before the caller writes it back to firmware.

Dependencies/integration: PnP core resource helpers, optional PCI IRQ penalization, packed `pnp_bios_node`, and PnP BIOS get/set callbacks.

Risks: parser uses direct unaligned casts like `*(short *)&p[4]`, which are x86-tolerated but nonportable; backend is x86_32 only. Length errors log but continue scanning. Encoding often sets min and max to the same assigned base and cannot represent all original range semantics. Resource stream must contain expected end tags or parse fails.

Test signals: synthetic streams with every supported tag, malformed lengths/no end tag, dependent option sets, compatible IDs and names, read-only parse vs full parse, and encode/decode round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpbios/rsparser.c -->
