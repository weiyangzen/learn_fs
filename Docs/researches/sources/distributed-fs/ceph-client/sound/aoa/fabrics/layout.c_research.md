# sources/distributed-fs/ceph-client/sound/aoa/fabrics/layout.c

## Purpose

This file implements the AOA layout fabric. It identifies supported Apple audio layouts from device-tree `layout-id` or `device-id`, requests matching codec modules, assigns codecs to soundbus/GPIO runtime data, creates output/detect ALSA controls, and manages autoswitching for headphone and line-out detection.

## Important APIs, types, and functions

Important data structures are `struct codec_connection`, `struct codec_connect_info`, `struct layout`, `struct layout_dev_ptr`, and `struct layout_dev`. Static layout tables map many PowerMac layout IDs and device IDs to codec names and connection bitmasks. Key functions are `find_layout_by_id`, `find_layout_by_device`, `use_layout`, `check_codec`, `layout_found_codec`, `layout_remove_codec`, `layout_notify`, `layout_attached_codec`, `aoa_fabric_layout_probe`, `aoa_fabric_layout_remove`, suspend/resume callbacks, and module init/exit.

## Control Flow

Soundbus probe locates a `soundchip` child node, reads layout or device ID, finds a layout table entry, allocates `layout_dev`, chooses feature-call or PMF GPIO methods, initializes GPIO, registers the AOA fabric, sets PCM name/id, requests required codec modules, and enables autoswitch defaults. When a codec registers, `layout_found_codec()` matches by name and optional OF phandle reference, assigns soundbus/GPIO pointers, computes codec-specific `connected` bits, and stores fabric data. After codec init, `layout_attached_codec()` creates amp/detect ALSA controls, registers notification callbacks, sets initial output state, and emits control notifications on jack changes.

## State and Persistence

The file uses global `layouts_list`, `layouts_list_items`, and singleton `layout_device`, matching the wider single-card AOA model. Each `layout_dev` persists while its soundbus device is bound and owns GPIO runtime state, control pointers, detect booleans, autoswitch flags, sound node reference, and layout pointer.

## Dependencies and Integration Points

It depends on the AOA core fabric API, soundbus driver API, OF node properties and phandles, `request_module`, ALSA controls, and PMF/feature GPIO methods. It also relies on codec drivers using names such as `onyx`, `tas`, `toonie`, and `topaz`.

## Risks and Test Signals

Risks include hard-coded layout data drift, singleton limitations, `layout_remove_codec()` not clearing codec array entries, autoswitch races, duplicate ALSA control names when lineout is labeled headphone, missing OF references with multiple soundbuses, and cleanup ordering with pending notifications. Tests should cover known layout IDs/device IDs, codec phandle matching, PMF vs feature GPIO selection, module request names, jack-detect autoswitch behavior, suspend/resume muting, and soundbus remove cleanup.
