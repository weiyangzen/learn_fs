# sources/distributed-fs/ceph-client/net/batman-adv/bat_iv_ogm.h

## Purpose
`bat_iv_ogm.h` exposes the BATMAN IV initialization entry point to the batman-adv core.

## Important API
- `batadv_iv_init(void)`: registers the BATMAN IV OGM receive handler and `BATMAN_IV` algorithm operations.

## Control Flow and Integration
Module initialization calls this header's single exported declaration. All other BATMAN IV implementation details remain private to `bat_iv_ogm.c`.

## State and Persistence
The header owns no state. Runtime state begins when `batadv_iv_init` registers handlers and algorithm ops.

## Risks and Test Signals
Risk is minimal and centers on init signature drift. Test signals include successful core initialization and BATMAN IV packet handler registration in builds with and without BATMAN V.
