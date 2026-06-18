# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_overlay.h

Purpose: Defines the hardware overlay representation and declares overlay management APIs used by plane and driver setup code.

Important APIs/types/functions: `struct omap_hw_overlay` stores index, name, DISPC plane ID, and caps. Declares init/destroy, assign/release, and state-update functions.

Control flow: Planes hold pointers to overlay objects in their private atomic state, while global atomic state maps overlay index to DRM plane for the next commit.

State and persistence: No storage here; structure instances are allocated by `omap_overlay.c` and referenced by plane state.

Dependencies and integration: Depends on OMAP DSS enum types from broader driver headers and DRM atomic plane concepts.

Risks: Header forward declarations omit some concrete types locally and rely on include ordering through `omap_drv.h`. Overlay pointers in duplicated plane state are shallow references and require stable overlay object lifetime until driver teardown.

Test signals: Build coverage and atomic state duplication/destruction tests that ensure overlay pointers remain valid.
