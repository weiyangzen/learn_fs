<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/packet-header-definitions.h -->
# sources/distributed-fs/ceph-client/drivers/firewire/packet-header-definitions.h

Purpose: provides inline field accessors for standard IEEE 1394 asynchronous packet headers and isochronous packet headers. It centralizes masks and shifts for on-bus big-picture packet fields so driver code and tests avoid open-coded bit manipulation.

Important APIs and control flow: asynchronous helpers operate on a four-quadlet `u32 header[ASYNC_HEADER_QUADLET_COUNT]`. Getters and setters cover destination, tlabel, retry, tcode, priority, source, response code, 48-bit offset split across header quadlets 1 and 2, quadlet data, data length, and extended tcode. Isochronous helpers operate on one `u32` and cover data length, tag, channel, tcode, and sy. Setters clear the target mask then OR the shifted field value back into the header.

State and persistence behavior: there is no mutable state. The header defines a stable internal interface for packet construction/parsing in FireWire code.

Dependencies and integration points: included by `ohci.c` for parsing received async packets and building local request handling, and by `packet-serdes-test.c` for round-trip validation. The tcode and rcode values come from FireWire constants supplied by callers.

Risks and test signals: the file has a duplicated `ASYNC_HEADER_Q1_RCODE_*` definition pair, which is harmless but a maintenance smell. Helpers do not validate field ranges, so high bits are silently masked. Endian expectations are caller-owned: these helpers operate on CPU-order `u32` packet header words, not `__be32` buffers. Test signals include KUnit async header cases for write/read/lock requests and responses, isochronous header round trips, and correct `ohci.c` behavior when parsing packet tcode, length, offsets, and response codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/packet-header-definitions.h -->
