# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v4.2.c

Purpose: Provides `ipa_data_v4_2`, the descriptor for IPA v4.2 hardware. It is an early v4 descriptor with the AP/modem endpoint topology, local memory layout, resource group programming, power data, and legacy IMEM/SMEM fallback addresses.

Important data: AP command TX uses channel 1 endpoint 6 and AP LAN RX uses channel 2 endpoint 8. AP modem TX/RX use channels 0/3 and endpoints 1/9. Modem command/LAN/AP endpoints are also represented so filtering and routing tables account for non-AP endpoints. Several hashed route/filter memory regions have size 0, indicating hash support is absent or disabled for this target. `ipa_data_v4_2` sets `version = IPA_VERSION_4_2`, `modem_route_count = 8`, 100 MHz core clock, 0x2000 IMEM, and 0x2000 SMEM.

Control flow and integration: The most important integration detail is in `gsi.c`: IPA v4.2 requires the AP to allocate modem channels with GSI generic commands, so modem endpoint entries in this descriptor feed `modem_channel_bitmap` during `gsi_channel_init()`. AP endpoints are initialized into GSI channels and command pools; modem endpoints are skipped for AP ring allocation but retained for IPA endpoint/filter bookkeeping.

State and persistence: The descriptor is immutable. Runtime state is created by consumers: endpoint bitmaps, channel maps, resource programming, and IPA-local memory table initialization. The AP modem-channel allocation quirk affects GSI hardware state during setup/teardown.

Dependencies: Requires v4.2-compatible endpoint names, IPA memory IDs, resource group IDs, GSI EE constants, and the v4.0 GSI register layout selected by `gsi_reg.c` for IPA v4.2.

Risks: Because v4.2 has the modem-channel allocation workaround, wrong modem channel IDs can cause generic command failures or leave modem channels unallocated. Zero-sized hashed memory regions must remain consistent with hash-support detection. TLV counts are lower than later platforms, so command channel validation must still satisfy `IPA_COMMAND_TRANS_TRE_MAX`.

Test signals: Logs should not show generic allocate/halt command failures for modem channels. Table initialization must tolerate zero hash sizes. Data path smoke should cover AP modem TX/RX, AP LAN RX, and modem restart/teardown to validate generic halt unwind.
