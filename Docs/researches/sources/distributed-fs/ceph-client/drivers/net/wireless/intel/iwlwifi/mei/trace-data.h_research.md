# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/trace-data.h

## Purpose

`trace-data.h` defines the iwlmei SAP data tracepoint when `CONFIG_IWLWIFI_DEVICE_TRACING` is enabled, and compiles to a no-op macro when tracing is disabled. It lets developers trace packet payload movement between CSME, the air interface, and DHCP TX mirroring without adding runtime instrumentation in normal builds.

## Important APIs, Types, and Functions

The exported macro/function interface is `trace_iwlmei_sap_data(skb, trace_type)`. `enum iwl_sap_data_trace_type` distinguishes RX-to-air packets, TX data from air, RX data dropped from air, and TX DHCP copies. `iwlmei_sap_data_offset()` chooses how much SAP header material to skip before copying packet bytes into the dynamic trace array.

## Control Flow

When tracing is enabled, the trace event copies `skb->len - offset` bytes from the skb into a dynamic trace payload and records the trace type. `main.c` emits this trace around shared-memory data queue writes, CSME-to-host transmissions, and drops; `net.c` indirectly uses it through `iwl_mei_add_data_to_ring()`.

## State and Persistence Behavior

There is no driver state. Trace records persist only in the kernel tracing buffers selected by the user. Offsets depend on the SAP wrapping type, so trace consumers see packet data rather than the SAP data header for most host-to-CSME cases.

## Dependencies and Integration Points

The header depends on tracepoint infrastructure, skb helpers, and `sap.h`. It is included by `trace.c` with `CREATE_TRACE_POINTS` and by instrumented code as a normal trace header.

## Risks and Edge Cases

Bad offset selection could make `skb_copy_bits()` read an invalid range, so every new SAP data wrapper type needs a matching offset rule and a disabled-tracing stub. Dynamic payload tracing can expose packet contents; enablement should be treated as debug-only.

## Test Signals

Build with tracing disabled to verify the no-op macro path, and with tracing enabled to verify tracepoint generation. Exercise all four trace types with packet sizes at and below wrapper lengths to catch offset issues.
