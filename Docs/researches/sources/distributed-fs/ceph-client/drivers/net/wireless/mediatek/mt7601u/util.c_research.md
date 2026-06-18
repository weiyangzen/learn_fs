# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/util.c

Purpose: Provides small skb utilities to insert and remove 2-byte padding when 802.11 headers are not 4-byte aligned for MT7601U DMA/TXWI requirements.

Important APIs and functions: `mt76_insert_hdr_pad()` ensures a misaligned 802.11 header gets two zero padding bytes after growing headroom with `skb_cow()`. `mt76_remove_hdr_pad()` reverses the transformation by moving the header forward and pulling two bytes.

Control flow: TX calls `mt76_insert_hdr_pad()` before pushing TXWI/DMA metadata. TX status cleanup calls `mt76_remove_hdr_pad()` if the restored skb header length is not 4-byte aligned. Both functions use `ieee80211_get_hdrlen_from_skb()` to determine whether padding is needed.

State and persistence: The only mutated state is skb data/headroom/length. No driver global state is touched.

Dependencies and integration points: Depends on mac80211 header length parsing and skb memory manipulation. Used by `tx.c` around DMA descriptor handling.

Risks: Incorrect memmove offsets would corrupt the 802.11 header. Insert/remove must stay symmetric with TXWI stripping or mac80211 will see malformed frames in status callbacks. `skb_cow()` failure must be propagated to free/drop the skb, which `tx.c` does.

Test signals: TX frames with both aligned and misaligned 802.11 header lengths, status callback skb integrity, and sanitizer checks around skb headroom validate these helpers.
