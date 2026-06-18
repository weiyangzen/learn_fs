# sources/distributed-fs/ceph-client/net/shaper/shaper_nl_gen.h

## Purpose
Auto-generated header for the net shaper generic-netlink family. It exposes generated policies, family descriptor, max handle id, and callback prototypes shared between generated netlink glue and the hand-written implementation.

## Important APIs, Types, And Functions
Declares `NET_SHAPER_MAX_HANDLE_ID`, policy arrays, pre/post doit and dump hooks, operation handlers for get/set/delete/group/capability commands, and `extern struct genl_family net_shaper_nl_family`.

## Control Flow
Included by both generated and hand-written shaper code. The generated source consumes callback prototypes; `shaper.c` implements them and registers the family at subsystem init.

## State And Persistence
No runtime state. It is compile-time interface glue derived from the YAML spec.

## Dependencies And Integration Points
Depends on generic netlink headers and `uapi/linux/net_shaper.h`. It must stay synchronized with `shaper_nl_gen.c`, the YAML spec, and `shaper.c`.

## Risks
Risks are interface drift, stale `NET_SHAPER_MAX_HANDLE_ID` relative to handle packing in `shaper.c`, and callback signature mismatch after netlink spec regeneration.

## Test Signals
Regeneration diff review, compile with `W=1`, validate handle id boundary tests, and ensure every declared callback has exactly one implementation.
