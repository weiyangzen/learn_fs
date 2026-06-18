# sources/distributed-fs/ceph-client/drivers/net/ethernet/rocker/rocker_tlv.c

Purpose: provides the out-of-line Rocker TLV parser and writer used by command, event, TX, and RX descriptor payload handling. It is intentionally narrow: parse an aligned TLV buffer into an indexed table and append one TLV to a descriptor buffer.

Important APIs: `rocker_tlv_parse()` clears a caller-provided table of `maxtype + 1` pointers, walks the TLV stream with `rocker_tlv_for_each()`, and stores TLVs whose type is within `1..maxtype`. `rocker_tlv_put()` checks descriptor tailroom, writes type/length, copies payload bytes, and zero-fills alignment padding.

Control flow: callers provide a descriptor data buffer and expected max type. Parse does no schema validation beyond the iterator's size checks and type bounds. Put calculates aligned total size from `rocker_tlv_total_size()`, appends at `rocker_tlv_start()`, advances `desc_info->tlv_size`, and returns `-EMSGSIZE` if the descriptor cannot hold the new attribute.

State and persistence: it only mutates the caller's descriptor TLV size and output parse table. No global state exists.

Dependencies and integration: depends on `rocker_tlv.h`, `rocker_hw.h`, `rocker.h`, string helpers, and errno. It is the common serialization path for Rocker command preparation and event/RX/TX parsing.

Risks: duplicate attribute types overwrite earlier entries in the parse table. Payload type, endian, and length validation are entirely caller-owned. `rocker_tlv_put()` assumes `data` is valid for nonzero `attrlen`, and zero-length nesting uses `NULL` safely only because memcpy length is zero.

Test signals: malformed length/alignment parsing, duplicate TLV type behavior, descriptor full path returning `-EMSGSIZE`, nested TLV construction, and all Rocker command/event schemas that depend on correct parse indices.
