# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/map.c

Purpose: implements AMD Address Translation Library DRAM map discovery and validation. It reads Data Fabric address-map registers for DF2, DF3, DF3.5, DF4, and DF4.5, finds the normalized-address map that contains the current address, and derives interleave properties needed by the later normalized-to-system translation path.

Important APIs and functions: the public entry point is `get_address_map(struct addr_ctx *ctx)`. It calls `get_address_map_common()`, `get_global_map_data()`, `dump_address_map()`, and `validate_address_map()`. Revision-specific helpers include `df2_get_dram_addr_map()`, `df3_get_dram_addr_map()`, `df4_get_dram_addr_map()`, `df4p5_get_dram_addr_map()`, and `df3_6ch_get_dram_addr_map()`. Interleave helpers include `get_intlv_mode()`, `get_num_intlv_chan()`, `get_intlv_bit_pos()`, `get_num_intlv_dies()`, `get_num_intlv_sockets()`, and `calculate_intlv_bits()`.

Control flow: `get_address_map_common()` first obtains the coherent-station fabric ID, searches DRAM offset registers for the active map, reads the map registers, validates the address range, and subtracts the normalized offset from `ctx->ret_addr`. Then `get_global_map_data()` decodes interleave mode, optional DF3 6-channel remap data, interleave bit position, die/socket counts, and total interleave bits. `validate_address_map()` rejects inconsistent combinations such as unsupported bit positions, die counts, socket counts, or invalid DF revision/mode encodings.

State and persistence: all state is transient in `ctx->map` and `ctx->ret_addr`; no persistent storage is used. Global hardware topology and revision data comes from `df_cfg`. Remap arrays are initialized to `0xff` before valid remap entries are populated because zero is a legal target.

Dependencies and integration: depends on `internal.h`, `reg_fields.h` masks, `df_indirect_read_instance()`, `df_indirect_read_broadcast()`, `FIELD_GET`, `order_base_2()`, and ATL debug helpers. It feeds downstream ATL translation and MI300 handling by producing a validated `dram_addr_map`.

Risks: register offsets and bit masks are highly revision-specific; a bad `df_cfg.rev` or heterogeneous MI300 flag changes shift widths and map-register locations. `find_normalized_offset()` assumes offsets are monotonic and nonzero when enabled. Unsupported interleave modes return errors; new hardware modes require updates in both field decoding and channel-count validation.

Test signals: exercise known DF2/DF3/DF4/DF4.5 systems, invalid map-valid bits, offset-disabled maps, monotonic offset violations, remap-enable paths, DF3 6-channel remap, MI300 heterogeneous offset shifts, and every interleave mode accepted by `get_num_intlv_chan()`.
