# sources/distributed-fs/ceph-client/sound/usb/implicit.c

## Purpose
Detects and configures implicit feedback synchronization for USB-audio formats, including generic UAC2 cases and vendor-specific quirks. It also selects a matching sync audioformat for implicit-feedback endpoints during PCM setup.

## Important APIs and Functions
`snd_usb_parse_implicit_fb_quirk()` mutates an `audioformat` to add sync endpoint/interface/altsetting fields when a quirk or generic rule applies. `snd_usb_find_implicit_fb_sync_format()` finds the best matching format for the sync endpoint. Helpers add fixed or generic sync endpoints, handle Roland/BOSS and Pioneer layouts, and score candidate formats by rate/format/channels.

## Control Flow
For playback endpoints, the parser first checks explicit quirk tables, then generic UAC2 implicit feedback, Roland/BOSS vendor-class pairs, Pioneer shared-altsetting layouts, and optional generic implicit feedback flags. For capture endpoints, only fixed capture quirks and Roland full-duplex support are handled; Pioneer capture skips generic handling. Adding a sync endpoint records endpoint number, interface, altsetting, endpoint index, and sets `fmt->implicit_fb`. Later, sync-format selection optionally falls back to the target when the same altsetting is shared, searches `chip->pcm_list` for a substream with matching endpoint and format type, and scores formats compatible with requested hw params.

## State and Persistence
State changes are confined to `audioformat` fields and sometimes `chip->quirk_flags` such as `QUIRK_FLAG_PLAYBACK_FIRST`. No persistent storage exists.

## Dependencies and Integration
Depends on USB descriptors, `card.h`, `helper.h`, PCM fixed-rate helper, and parsed PCM stream lists. Endpoint code consumes `fmt->implicit_fb` and sync fields to link endpoints and drive packet sizes from capture feedback.

## Risks and Test Signals
Risks include incorrect endpoint/interface assumptions for vendor-specific devices, missing capture quirk table entries, shared-altsetting fallback choosing an incompatible format, and `fixed_rate` assignment when no substream is found. Tests should cover known M-Audio, MOTU, Roland/BOSS, Pioneer, Yamaha/Steinberg/Fractal/SSL/Zoom devices, generic UAC2 implicit feedback descriptors, and full-duplex open with matching/mismatched rates and channel counts.
