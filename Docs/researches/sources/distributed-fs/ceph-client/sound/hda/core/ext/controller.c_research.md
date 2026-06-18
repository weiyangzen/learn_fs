# sources/distributed-fs/ceph-client/sound/hda/core/ext/controller.c

## Purpose
`ext/controller.c` implements extended HD-audio controller helpers for processing-pipe capability, multilink discovery, link power/refcount control, stream ID routing to links, and codec-link power integration.

## Important APIs, Types, and Functions
Exports include `snd_hdac_ext_bus_ppcap_enable()`, `snd_hdac_ext_bus_ppcap_int_enable()`, `snd_hdac_ext_bus_get_ml_capabilities()`, `snd_hdac_ext_link_free_all()`, hlink lookup helpers by id/address/name, link power up/down/all, stream-id set/clear, `snd_hdac_ext_bus_link_get()`, `snd_hdac_ext_bus_link_put()`, and `snd_hdac_ext_bus_link_power()`.

## Control Flow
ML capability parsing reads link count, allocates `hdac_ext_link` objects, records link registers/capabilities/address masks, optional alternate-link IDs, initial refcount, and appends them to `hlink_list`. Link get increments refcount; a 0-to-1 transition starts command DMA if needed, powers the link, clears output stream routing, waits for codec status, and updates `codec_mask`. Link put powers down on 1-to-0 and stops command DMA when all links are off.

## State and Persistence Behavior
Persistent state is the hlink list, each link’s refcount, register base, capabilities, stream masks, and bus command-DMA state. `codec_powered` remains the generic power bitset and is synchronized with extended link up/down.

## Dependencies and Integration Points
The file depends on HDA extended register definitions, base command I/O helpers, `bus->mlcap` from capability parsing, and codec device names of the form `ehdaudio%dD%d`.

## Risks
Reference counting must not underflow; link get/put assume balanced codec/stream users. Command DMA is stopped when no links are up, so late commands require link reacquisition. Name parsing limits address to 0..31 and assumes stable device naming. ML capability pointer must be valid before use.

## Test Signals
Test ML capability parsing, hlink lookup modes, link power CPA polling, command-DMA start/stop across multiple links, stream ID routing registers, codec power transitions, and balanced refcounts under concurrent users.
