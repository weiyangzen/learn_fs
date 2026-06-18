# sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_tlv.h

Purpose: defines the Rocker TLV wire layout helpers, alignment rules, typed accessors, parse wrappers, append wrappers, and nested attribute helpers used throughout the Rocker driver.

Important APIs: alignment is fixed at 8 bytes via `ROCKER_TLV_ALIGNTO`; `ROCKER_TLV_HDRLEN` is the aligned `struct rocker_tlv` size. Iteration uses `rocker_tlv_ok()`, `rocker_tlv_next()`, `rocker_tlv_for_each()`, and `rocker_tlv_for_each_nested()`. Accessors include `rocker_tlv_type()`, `rocker_tlv_data()`, `rocker_tlv_len()`, and typed getters for u8/u16/be16/u32/u64. Writers include `rocker_tlv_put_u8/u16/be16/u32/be32/u64()`, `rocker_tlv_nest_start()`, `rocker_tlv_nest_end()`, and `rocker_tlv_nest_cancel()`.

Control flow: command builders append fields by repeatedly calling typed put helpers. Nested commands reserve an empty TLV, append children, then patch the parent length at nest end. Cancel resets `desc_info->tlv_size` to the nested TLV start.

State and persistence: this header owns no state. It manipulates caller-owned descriptor buffers and relies on descriptor `data_size`, `tlv_size`, and `desc->tlv_size` for bounds and parsing.

Dependencies and integration: directly includes Rocker hardware and core structures, so it is tightly coupled to descriptor layout. It underpins Rocker command prep, command response parsing, event parsing, and TX/RX fragment descriptors.

Risks: typed getters cast directly from unaligned-looking payload addresses, relying on the 8-byte-aligned TLV header/data layout. There is no endian conversion for host-order getters. Nest length patching assumes no concurrent mutation of the descriptor. `rocker_tlv_parse_desc()` trusts `desc_info->desc->tlv_size`, so corrupted hardware writeback can affect parsing until iterator bounds stop it.

Test signals: compile coverage on architectures with strict alignment, nested cancel/end behavior, parsing of zero-length and padded attributes, and command builders that fill descriptors near capacity.
