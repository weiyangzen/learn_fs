# sources/distributed-fs/ceph-client/include/ras/ras_event.h

Purpose: declares RAS tracepoints for memory-controller errors, ACPI CPER extended memory errors, ARM processor errors, non-standard CPER sections, and PCIe AER errors. It is a trace-event schema header included by tracepoint users and by `trace/define_trace.h`.

Important APIs and types: `TRACE_EVENT(extlog_mem_event)` is ACPI extlog-gated and records sequence, CPER memory error type/severity, physical address/mask, FRU GUID/text, and packed compact memory-error data. `TRACE_EVENT(mc_event)` records EDAC-style memory-controller error type, labels, count, hierarchy location, address/grain/syndrome, and driver detail. `TRACE_EVENT(arm_event)` records CPER ARM processor fields, raw processor/context/OEM buffers, severity, and CPU. `TRACE_EVENT(non_standard_event)` records section GUID, FRU, severity, raw payload length, and bytes. `TRACE_EVENT(aer_event)` is `CONFIG_PCIEAER` gated and records device, status bits, severity, optional TLP header, and bus type with correctable/uncorrectable flag decoding tables.

Control flow: RAS, EDAC, ACPI/APEI, ARM CPER, and PCIe AER handlers call generated tracepoint functions when hardware reports corrected or uncorrected events. Each `TP_fast_assign` copies validated fields and raw buffers into the ring buffer, and `TP_printk` formats them for tracefs/perf/ftrace consumers.

State and persistence: the header owns no persistent state. Event data is transient trace-buffer data; CPER validation bits decide whether fields are stored or replaced with sentinel values. Trace buffers and userspace collection determine retention.

Dependencies and integration points: depends on Linux tracepoint macros, EDAC helpers, CPER structures/formatters, PCI/AER constants, GUID handling, ktime-related trace support, and `trace/define_trace.h`. It is the common observability contract across hardware error subsystems.

Risks and test signals: risks include copying raw dynamic arrays with unvalidated lengths, stale CPER validation-bit handling, formatting mismatches for GUIDs/TLP headers, config-gated tracepoint build drift, and trace ABI field-name changes breaking tooling. Test with trace-event compile checks under ACPI_EXTLOG/PCIEAER on/off, synthetic EDAC events, CPER ARM/non-standard injection, AER injection, tracefs format verification, and perf/ftrace decoding.
