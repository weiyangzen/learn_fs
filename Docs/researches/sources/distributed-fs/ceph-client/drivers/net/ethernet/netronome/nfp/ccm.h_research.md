<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm.h

## Purpose
This header defines the common NFP control-message ABI and transport state. It enumerates firmware message types for BPF maps/events and crypto operations, defines the shared control-message header and TLV constants, provides inline accessors for skb type/tag fields, declares `struct nfp_ccm`, and exposes CCM transport and mailbox helper APIs.

## Important APIs, Types, And Functions
- `enum nfp_ccm_type` assigns request ids for BPF map alloc/free/lookup/update/delete/getnext/getfirst, BPF events, and crypto reset/add/delete/update/resync.
- `NFP_CCM_ABI_VERSION`, `NFP_CCM_TYPE_REPLY_BIT`, and `__NFP_CCM_REPLY()` define the request/reply ABI convention.
- `struct nfp_ccm_hdr` is the firmware header containing type, version, and big-endian tag, also viewable as a raw 32-bit word.
- Inline helpers `nfp_ccm_get_type()`, `__nfp_ccm_get_tag()`, and `nfp_ccm_get_tag()` decode skb headers.
- `enum nfp_ccm_mbox_tlv_type` and `NFP_NET_MBOX_TLV_*` define mailbox TLV framing constants used by mailbox-backed CCM paths.
- `struct nfp_ccm` stores app pointer, tag allocator bitmap/cursors, reply queue, and waitqueue.
- Prototypes expose skb-based CCM and mailbox-backed communication helpers.

## Control Flow
The header's ABI is used by callers that allocate an skb with room for `struct nfp_ccm_hdr`, fill request-specific payload after the header, and call `nfp_ccm_communicate()` or mailbox variants. Firmware replies set the reply bit in the type and echo the tag; receive handlers use the inline helpers to route the skb to the matching waiter or event path.

## State And Persistence
No storage is defined beyond `struct nfp_ccm` instances embedded in app or netdev private state. Tags and reply queues are runtime-only. Firmware message type ids and header layout are persistent ABI contracts between driver and firmware.

## Dependencies And Integration Points
It includes Linux bitmap, skb, and waitqueue headers and forward-declares `struct nfp_app` and `struct nfp_net`. BPF control messages include this header through `fw.h`; app control receive code calls `nfp_ccm_rx()`; mailbox helpers integrate CCM with NFP netdev mailbox transport.

## Risks And Edge Cases
- Type ids are ABI values; changing or reordering the enum breaks firmware compatibility.
- `struct nfp_ccm_hdr` relies on exact byte layout and big-endian tag encoding.
- The tag bitmap has `U16_MAX + 1` bits, so cursor wraparound behavior must match unsigned 16-bit arithmetic in the implementation.
- Mailbox TLV declarations here are only framing constants; callers must still validate actual mailbox sizes and maximum reply lengths.

## Test Signals
Build users of skb and mailbox CCM paths, verify request/reply type ids against firmware, test tag encode/decode, BPF map operations over CCM, BPF event messages bypassing reply matching, mailbox TLV parsing for supported/unsupported message types, and cleanup with empty reply queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm.h -->
