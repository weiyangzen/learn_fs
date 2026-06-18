# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v5.2.c

Purpose: Exports `ipa_data_v5_2`, the static IPA v5.2 configuration for endpoint, resource, memory, QSB, and power setup.

Important data: AP command TX uses channel 6 endpoint 9, AP LAN RX channel 7 endpoint 11, AP modem TX channel 5 endpoint 2, and AP modem RX channel 9 endpoint 18. AP modem TX uses 512 TRE/event entries and TLV count 25. Modem route count is 11. Unlike v5.0/v5.5, this descriptor no longer supplies deprecated IMEM address/size fallback values, but it does specify SMEM 0xb000. Memory includes v5-sized route tables, modem/AP headers, large modem proc context, quota/tethering/filter-route/drop stats, modem memory, NAT, and PDN config.

Control flow and integration: The descriptor is consumed by the same v5 register and command paths as v5.0. The absence of IMEM fallback means DT-provided IMEM is expected. GSI setup uses v5 event-count discovery and v5 channel context fields. IPA command code uses full-byte endpoint encoding and validates the v5 memory offsets.

State and persistence: Immutable source tables. Runtime state is allocated and programmed by IPA/GSI setup and torn down through the common driver.

Dependencies: Requires DT to provide memory resources that older descriptors could fall back to in this file. Depends on v5.0 GSI register definitions, endpoint/memory enum stability, and power/interconnect bindings.

Risks: v5.2 mixes v5 GSI behavior with endpoint/channel IDs that differ from v5.0/v5.5. Missing IMEM fallback can expose DT regressions. Route/filter region sizes and offsets are close together and canary-protected, so manual edits need overlap checks.

Test signals: Probe with v5.2 DT should not require descriptor IMEM fallback. IPA memory validation, command pipeline clear, AP modem traffic, and modem SSR should pass. Watch for DT memory resource errors, GSI command timeouts, and table init region overflow logs.
