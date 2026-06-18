# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v3.5.1.c

Purpose: Supplies the static `ipa_data_v3_5_1` platform descriptor consumed by the IPA probe/match path. It binds IPA v3.5.1 hardware to QSB bus tuning, endpoint-to-GSI-channel mappings, resource group limits, IPA-local memory layout, deprecated IMEM/SMEM fallback addresses, and power/interconnect votes. The file has no runtime functions; its behavior is expressed through immutable tables.

Important data: `ipa_qsb_data` defines DDR/PCIE outstanding read/write limits, without `max_reads_beats` because this version predates that field. `ipa_gsi_endpoint_data` maps AP command TX, AP LAN RX, AP modem TX/RX, and modem-owned endpoints to concrete EE IDs, GSI channel IDs, IPA endpoint IDs, directions, TRE/event counts, TLV FIFO depths, and endpoint config. AP modem TX and modem TX paths mark `filter_support`. The exported `ipa_data_v3_5_1` sets `version = IPA_VERSION_3_5_1`, a nonzero `backward_compat` mask for legacy BCR quirks, `modem_route_count = 8`, and pointers to all local tables.

Control flow and integration: `ipa_main` selects this descriptor from Device Tree compatible data, then `gsi_init()` consumes `endpoint_count`/`endpoint_data` to allocate AP GSI rings and validate TRE/event/TLV constraints. IPA memory setup uses the memory descriptors for filter, route, header, proc context, modem, and microcontroller event-ring regions. Command setup validates table/header regions against the immediate-command field widths.

State and persistence: The file contributes no mutable state. Its constants become boot-time configuration for in-memory `struct ipa`, `struct gsi_channel`, endpoint bitmaps, DMA ring allocation sizes, and IPA-local memory programming. Persistence is hardware state after setup, not file-local storage.

Dependencies: Includes Linux bit helpers plus IPA headers for endpoint, memory, power, register, resource, and version constants. It depends on `ipa_data.h` struct layouts and on enum values in endpoint/memory headers remaining stable.

Risks: Channel IDs, endpoint IDs, and memory offsets are silicon-contract values; a single wrong number can silently route traffic to the wrong endpoint or corrupt IPA-local tables. `backward_compat` bits are version-specific and must not be copied to newer descriptors. IMEM/SMEM values are deprecated fallback data and should match older DT consumers only.

Test signals: Probe should accept the v3.5.1 compatible, GSI setup should not reject power-of-two rings or TLV limits, IPA memory validation should pass canary layout checks, and modem data path smoke tests should exercise AP modem TX/RX plus AP LAN RX. Regression logs to watch include GSI bad channel state, table-region size/offset errors, and BCR programming failures.
