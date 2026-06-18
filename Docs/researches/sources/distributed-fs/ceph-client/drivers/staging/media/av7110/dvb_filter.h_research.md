# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/dvb_filter.h

## Purpose
This header defines the stream constants and small state structures shared by the AV7110 MPEG repacker/filter helpers. It covers MPEG PES stream IDs, MPEG video start codes, PTS/DTS flags, TS packet flags, adaptation flags, packet length limits, the `ipack` parser state, video/audio metadata structures, and PES-to-TS callback APIs.

## Important APIs and Types
`dvb_filter_pes2ts_cb_t` and `struct dvb_filter_pes2ts` define the packetizer callback contract. Function declarations are `dvb_filter_pes2ts_init()`, `dvb_filter_pes2ts()`, and `dvb_filter_get_ac3info()`.

`struct ipack` is the central state object used by `av7110_ipack.c`; it contains parser counters, PES IDs and length bytes, header flags, PTS buffer, callback fields, caller data, and `repack_subids`. `struct dvb_video_info`, `struct mpg_picture`, and `struct dvb_audio_info` describe parsed media metadata for legacy filter users.

## Control Flow and State
The header itself has no runtime flow, but it defines state machines consumed elsewhere. `struct ipack` records incremental PES parser state across byte chunks. `struct dvb_filter_pes2ts` records TS continuity state across PES packetization calls. Constants such as `MAX_PLENGTH`, `MMAX_PLENGTH`, and `IPACKS` bound parser behavior.

## Dependencies and Integration Points
It includes `<linux/slab.h>` and `<media/demux.h>`, and is included by AV7110 repacker and DVB filter implementation. It is legacy media helper infrastructure, with names overlapping generic DVB concepts but scoped here under the AV7110 staging tree.

## Risks and Test Signals
Risks include ABI-like coupling because parser code relies on exact field names and constants, weak type encapsulation, and large length constants permitting substantial buffer requirements. Test signals come from compiling all consumers, exercising PES parser state transitions, AC3 info parsing, TS packetization, and validating media metadata users if enabled.
