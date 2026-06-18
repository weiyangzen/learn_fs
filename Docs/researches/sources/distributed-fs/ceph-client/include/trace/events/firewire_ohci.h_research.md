<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/firewire_ohci.h -->
# sources/distributed-fs/ceph-client/include/trace/events/firewire_ohci.h

## Purpose
Declares OHCI-1394 controller tracepoints for interrupt events and self-ID completion data.

## APIs, Control Flow, and State
`irqs` records a controller card index and an OHCI event bitmask, formatting notable bits such as self-ID completion, async request/response packets, transmit completions, isochronous RX/TX, posted write errors, cycle timer anomalies, register access failure, unrecoverable errors, and bus reset. `self_id_complete` records the card index, SelfIDCount register, and a dynamic array of self-ID receive quadlets sized by `ohci1394_self_id_count_get_size(reg)`. Helper macros decode self-ID error state, generation, receive generation, and timestamp; `cond_le32_to_cpu()` handles the big-endian header quirk before trace storage. No controller state is owned by the header.

## Dependencies, Integration, Risks, and Tests
Depends on OHCI1394 register constants and helper functions defined in `drivers/firewire/ohci.c` or nearby headers, plus tracepoint support. Integration points are OHCI interrupt handling and self-ID buffer completion after bus resets. Risks include dynamic-array sizing trusting register contents, endian quirk handling mistakes, reading empty self-ID buffers while formatting index zero, and losing interrupt sequencing if event bits are coalesced. Test signals include OHCI interrupt tracing during device activity, bus reset/self-ID completion tests, controllers with and without the big-endian header quirk, malformed self-ID error paths, and compile checks when OHCI bit definitions change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/firewire_ohci.h -->
