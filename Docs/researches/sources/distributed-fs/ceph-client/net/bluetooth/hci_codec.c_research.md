# sources/distributed-fs/ceph-client/net/bluetooth/hci_codec.c

## Purpose
This file discovers local Bluetooth controller codec support and codec capabilities through HCI commands and stores the results in the HCI device codec list.

## Important APIs, Types, And Functions
Public functions are `hci_read_supported_codecs()`, `hci_read_supported_codecs_v2()`, and `hci_codec_list_clear()`. Internal helpers are `hci_codec_list_add()` and `hci_read_codec_capabilities()`. The code populates `struct codec_list` entries in `hdev->local_codecs`.

## Control Flow
The v1 and v2 entry points send synchronous Read Local Supported Codecs commands, validate response sizes, parse standard and vendor codec arrays, and request capabilities for each supported transport. `hci_read_codec_capabilities()` iterates transport bits, falls back to adding codecs without caps if the controller lacks the Read Codec Capabilities command, otherwise sends the command, validates status and variable-length capability records, and appends a codec-list entry under `hci_dev_lock()`. Clearing walks and frees all list entries.

## State, Persistence, And Dependencies
State persists in `hdev->local_codecs` until cleared, typically across HCI device setup lifetime. Each list entry stores codec ID, optional company/vendor IDs, transport, capability count, and variable-length capability bytes. The file depends on synchronous HCI command helpers, HCI command bitmasks, flexible-array response structs, and HCI device locking.

## Integration Points
HCI initialization/setup code calls these functions after reading controller features. Management or debug paths can later report `hdev->local_codecs` to userspace. The header declares these functions for HCI core users.

## Risks
All parsing is from controller-provided variable-length data; missed length validation could overrun. Current code validates aggregate codec arrays and each capability record before copying. Capability command failures skip that codec/transport rather than aborting discovery. If list clearing is omitted during device reset, stale codec entries could be reported.

## Test Signals
Signals include correctly populated standard and vendor codec entries for v1/v2 responses, no-cap fallback when command bit is absent, rejection of short or malformed responses, no leaks after `hci_codec_list_clear()`, and management output matching controller-advertised codecs.
