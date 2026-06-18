<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/mac.h

## Purpose
This header declares pureLiFi mac80211-private structures, rate constants, USB TX control header layout, RX/TX status overlays, beacon state, device flags, conversion helpers, and public MAC-layer APIs.

## Important APIs, Types, And Functions
It defines pureLiFi CCK/OFDM rate encodings, modulation-rate enum values, regulatory constants, `struct plfxlc_ctrlset`, `struct plfxlc_header`, `struct tx_status`, `struct beacon`, `enum plfxlc_device_flags`, and `struct plfxlc_mac`. Inline helpers convert between `ieee80211_hw`, chip, USB, and MAC containers and retrieve the permanent MAC address. API prototypes cover hardware allocation/release, preinit/init, RX, TX completion, start/stop, and restore.

## Control Flow
The inline helpers are used throughout USB and chip callbacks to recover enclosing objects. `struct plfxlc_ctrlset` is prepended to every outgoing frame by `mac.c`, and `struct tx_status` is available for completion status interpretation.

## State And Persistence
`struct plfxlc_mac` is the private state allocated with `ieee80211_alloc_hw()`. It persists active VIF, beacon work/cache fields, multicast hash, ACK queue, channels/rates/band, embedded chip/USB state, hardware/serial addresses, pass flags, association state, type, RSSI, and CRC counters.

## Dependencies And Integration Points
Includes Linux mac80211 and `chip.h`. Used by `mac.c`, `usb.c`, `chip.c`, and firmware helpers. The declared control header and status structures must match device firmware expectations.

## Risks
Packed overlay structures mix protocol fields and host pointers; misuse could treat packet bytes as pointers. Some declared work fields are not actively used in the current implementation. Rate constants and LC band setup must align with mac80211 expectations and firmware rate IDs.

## Test Signals
Build coverage catches API drift. Runtime validation includes TX header acceptance by firmware, RX/TX completion behavior, ethtool stats, object container conversions during USB callbacks, and clean hardware release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/mac.h -->
