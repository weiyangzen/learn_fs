<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/chip.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/chip.h

## Purpose
This header declares the pureLiFi chip wrapper, radio/unit enums, multicast hash helper, and chip-level control APIs used by the mac80211 and USB layers.

## Important APIs, Types, And Functions
It defines `enum unit_type`, radio constants `PLFXLC_RADIO_OFF` and `PLFXLC_RADIO_ON`, `struct plfxlc_chip`, `struct plfxlc_mc_hash`, `plfxlc_chip_dev()`, API prototypes for chip init/release/RXTX/rate/beacon/radio control, `plfxlc_usb_to_chip()`, and `plfxlc_mc_add_all()`.

## Control Flow
The inline helpers convert from embedded USB object to chip object and set multicast hash fields to all ones. All other execution is in `chip.c`.

## State And Persistence
`struct plfxlc_chip` embeds `struct plfxlc_usb`, a mutex, unit type, link LED, and beacon interval cache. It is embedded in `struct plfxlc_mac`, so its lifetime follows the mac80211 hardware object.

## Dependencies And Integration Points
Includes mac80211 and `usb.h`. It is included by `chip.c`, `mac.c`, and `usb.c`, making it the local bridge between MAC and USB transport state.

## Risks
Because `chip.h` includes `usb.h` and `usb.h` references chip/mac conversion helpers elsewhere, include ordering must avoid circular compile issues. The multicast helper blindly enables all hash bits and depends on firmware interpretation.

## Test Signals
Compile coverage and runtime probe/release validate structure layout and conversion helpers. Multicast filter tests validate `plfxlc_mc_add_all()` through `configure_filter()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/chip.h -->
