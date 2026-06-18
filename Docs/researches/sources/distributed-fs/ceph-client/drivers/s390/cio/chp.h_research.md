# sources/distributed-fs/ceph-client/drivers/s390/cio/chp.h

## Purpose
This header defines the channel-path data model and public helpers used by s390 CIO, CSS, and CHSC code to track channel-path identity, status, descriptions, measurement characteristics, and path links.

## Important APIs, Types, and Functions
It defines status constants (`CHP_STATUS_*`), event constants (`CHP_ONLINE`, `CHP_OFFLINE`, `CHP_VARY_ON`, `CHP_VARY_OFF`, `CHP_FCES_EVENT`), `struct chp_link`, and `struct channel_path`. `channel_path` embeds a Linux device, channel-path id, mutex-protected descriptors (`fmt0`, `fmt1`, `fmt3`), logical state, CMG capability flags, speed, and measurement-characteristic blocks. `chp_test_bit()` reads SCLP/CHSC bitmaps, and `chpid_to_chp()` maps a `chp_id` into the active CSS channel-path table.

## Control Flow
The header contains no standalone execution, but callers use it to move between hardware IDs and registered kernel objects. CHSC/CSS/device event code builds `struct chp_link` values, resolves them with `chp_ssd_get_mask()`, and calls channel-path APIs to update descriptors, schedule configuration, or compute operational path masks.

## State and Persistence
The header declares volatile in-kernel structures only. `chpid_to_chp()` assumes the singleton `css_by_id()` model and that `channel_subsystems[0]` is initialized. No persistent storage is defined.

## Dependencies and Integration Points
It depends on Linux device/mutex types, `asm/chpid.h`, `chsc.h`, and `css.h`. It is the contract shared by `chp.c`, `chsc.c`, `css.c`, `device.c`, and measurement code.

## Risks and Test Signals
Risk areas are singleton-CSS assumptions, direct array indexing by hardware ids, and declaration drift between channel-path structures and CHSC descriptor formats. Test signals are compile coverage of all includers, channel-path registration with valid and invalid CHPID values, and path-event propagation using full and partial FLA masks.
