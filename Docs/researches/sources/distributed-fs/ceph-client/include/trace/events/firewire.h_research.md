<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/firewire.h -->
# sources/distributed-fs/ceph-client/include/trace/events/firewire.h

## Purpose
Defines high-level FireWire core tracepoints for asynchronous transactions, PHY packets, bus reset handling, self-ID packets, isochronous context allocation/lifecycle, packet queueing, and completion reporting.

## APIs, Control Flow, and State
The header provides bit-extraction helpers for async packet headers and PHY self-ID fields. Event classes cover async outbound initiation/completion, async inbound packets, bus reset arrangement, isochronous destroy/start/stop/flush/completion templates, and single-completion templates. Concrete events include async request/response outbound/inbound initiation/completion, PHY outbound/inbound, `bus_reset_initiate/schedule/postpone/handle`, `self_id_sequence`, isochronous outbound/inbound allocation and destruction, multiple-channel reporting, start/stop/flush/flush_completions, outbound and inbound queue events, outbound/inbound single completions, and inbound multiple completions. Conditional events suppress disabled or irrelevant isochronous traces. The header stores no FireWire state; it snapshots card index, transaction labels/codes, node IDs, offsets, rcodes, packet quadlets, bus-generation metadata, channel/speed/tag/sync fields, and context-completion causes.

## Dependencies, Integration, Risks, and Tests
Depends on FireWire core packet formats, isochronous context structures, tracepoint macros, and constants defined by FireWire headers or including translation units. Integration points are transaction layer send/receive, bus reset scheduling and handling, self-ID processing, and isochronous DMA queue/completion paths. Risks include packet-format drift, endian or quadlet-order mistakes, high trace volume for isochronous streaming, exposing bus topology/addresses, and conditional events hiding state when contexts are not enabled. Test signals include FireWire transaction tests, bus reset/self-ID traces, isochronous streaming under trace, PHY packet injection, completion cause coverage, and build checks after packet macro changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/firewire.h -->
