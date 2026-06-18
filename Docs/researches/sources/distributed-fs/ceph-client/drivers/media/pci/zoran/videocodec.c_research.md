# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/videocodec.c

## Purpose
`videocodec.c` implements a small in-driver registry that binds Zoran master devices to hardware codec implementations. Codec templates register once, masters attach to matching templates, and each attachment receives a duplicated `struct videocodec` with per-attachment private data.

## Important APIs, Types, And Functions
Internal lists are `struct codec_list` for registered codec templates and `struct attached_list` for live attachments. Global state is `codeclist_top`. Exported functions are `videocodec_attach()`, `videocodec_detach()`, `videocodec_register()`, `videocodec_unregister()`, and `videocodec_debugfs_show()`. Attach uses `kmemdup()` on the template, appends an instance suffix to `codec->name`, sets `codec->master_data`, and calls the codec's `setup()` callback. Detach calls `unset()`, unlinks the attachment, frees the duplicated codec, and decrements `attached`.

## Control Flow
Codec implementations call `videocodec_register()` from their init helpers. During PCI probe, `zoran_card.c` builds a `struct videocodec_master` with bus read/write callbacks and calls `videocodec_attach()`. Attach scans registered templates and accepts one where `(master->flags & codec->flags) == master->flags`, then invokes setup to verify hardware and allocate private state. Driver removal calls `videocodec_detach()` and later unregisters templates through codec cleanup helpers.

## State And Persistence
All state is in global linked lists and dynamically allocated codec instances. There is no locking in this file, so it assumes serialized registration/attachment through the driver probe/remove path. Debugfs rendering walks the same lists and prints registered templates plus attached masters.

## Dependencies And Integration Points
This layer depends on `videocodec.h` callbacks, Zoran logging helpers via `videocodec_to_zoran()`, and codec implementations in `zr36016.c`, `zr36050.c`, and `zr36060.c`. It bridges the master bus access functions in `zoran_card.c` with codec-specific register programming.

## Risks
The matching expression requires the codec flags to include every flag requested by the master, but it does not check codec type directly; card probe performs type validation after attach. Lack of locking would be unsafe if multiple probe/remove or debugfs paths could concurrently mutate/traverse the lists. `videocodec_register()` derives a Zoran pointer from a template codec that may not yet have master data, so logging paths rely on current assumptions about call context.

## Test Signals
Probe logs should show codec registration and attachment, debugfs should list slave templates and master attachments, and removal should not leave `attached` counts behind. Negative tests include absent codec support, wrong type after attach, busy unregister while attached, and attach failure from codec `setup()`.
