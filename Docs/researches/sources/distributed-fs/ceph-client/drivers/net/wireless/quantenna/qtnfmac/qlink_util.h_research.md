## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/qlink_util.h

### Purpose
`qlink_util.h` declares QLINK conversion helpers and provides inline TLV append/iteration utilities for command skb construction and response parsing.

### Important APIs, Types, And Functions
Inline helpers are `qtnf_cmd_skb_put_buffer()`, `qtnf_cmd_skb_put_tlv_arr()`, and `qtnf_cmd_skb_put_tlv_u32()`. It declares the conversion functions implemented in `qlink_util.c`. Macros `qlink_for_each_tlv()` and `qlink_tlv_parsing_ok()` implement aligned TLV walking and final-position validation.

### Control Flow
The skb helpers append raw data or TLV headers plus values to an skb. TLV arrays round payload allocation up to `QLINK_ALIGN` while storing the original unpadded length in the header. The iteration macro advances by `sizeof(*tlv) + round_up(len, QLINK_ALIGN)` only while enough bytes remain for both header and declared value.

### State, Persistence, And Dependencies
There is no state. The header depends on skb APIs, cfg80211, QLINK wire definitions, endian helpers, and the caller maintaining sufficient skb tailroom. The persistent effect is serialized QLINK TLV payload in command skbs.

### Integration Points
Command builders use the skb append helpers for IE, bitmap, key, WoWLAN, and regulatory TLVs. Parsers use the TLV loop while processing firmware responses and events.

### Risks
The inline TLV append helper does not explicitly zero alignment padding, so consumers must respect `len` rather than padded bytes. Tailroom is assumed. `qlink_tlv_parsing_ok()` compares against rounded total length, so callers must pass the same logical length convention used by the firmware payload.

### Test Signals
Useful tests include TLV arrays with unaligned lengths, zero-length TLVs, malformed length overruns, exact-end parsing, skb tailroom assertions, and endian checks for u32 TLVs.
