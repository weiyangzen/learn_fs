# sources/distributed-fs/ceph-client/drivers/scsi/libfc/fc_frame.c

Purpose: provides the small frame allocation and CRC helper layer used by libfc. It creates transmit `fc_frame` objects backed by sk_buffs with libfc headroom/tailroom and verifies received frame CRCs when hardware or the lower layer has left the CRC unchecked.

Important APIs/types/functions: `fc_frame_crc_check()` clears `FCPHF_CRC_UNCHECKED`, recomputes the Fibre Channel CRC over the header plus payload rounded to a 4-byte fill boundary, and returns the XOR error value. `_fc_frame_alloc()` allocates an fclone skb with `FC_FRAME_HEADROOM`, `FC_FRAME_TAILROOM`, and `NET_SKB_PAD`, initializes it as an `fc_frame`, and sizes it for the FC header plus payload. `fc_frame_alloc_fill()` adds zero fill for non-4-byte payloads, allocates through `_fc_frame_alloc()`, then trims the visible skb length back to the requested header plus payload length.

Control flow: callers normally use higher-level `fc_frame_alloc()` or `fc_frame_alloc_fill()` from protocol code. For transmit, allocation reserves headroom, casts the skb storage to `struct fc_frame`, initializes frame metadata, and grows the skb to include header and payload. For receive validation, `fc_frame_crc_check()` assumes a linear frame, computes CRC from `fr_hdr(fp)` over padded length, compares it to `fr_crc(fp)`, and returns zero on match.

State and persistence: there is no persistent or global state. The functions manipulate per-frame skb length, metadata flags, and fill bytes. Allocations are atomic (`GFP_ATOMIC`) because frames are often created from softirq or protocol callback contexts.

Dependencies and integration: depends on Linux sk_buff/fclone allocation, CRC32, and `scsi/fc_frame.h` accessors. It is used by the FCP path, ELS/CT builders, exchange code, and response helpers that need correctly padded Fibre Channel frames.

Risks and test signals: `_fc_frame_alloc()` warns on unaligned payload sizes, while `fc_frame_alloc_fill()` handles unaligned payloads by padding and trimming; callers must choose the right helper. CRC checking warns if the skb is non-linear, so lower layers must linearize before asking software to verify CRC. Test zero-length payloads, non-4-byte payload fill, allocation failure paths, CRC success/failure with fill bytes, and callers that pass fragmented frames with `FCPHF_CRC_UNCHECKED`.
