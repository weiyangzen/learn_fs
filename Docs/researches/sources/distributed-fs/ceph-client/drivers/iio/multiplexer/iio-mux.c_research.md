# sources/distributed-fs/ceph-client/drivers/iio/multiplexer/iio-mux.c

## Purpose
Platform driver that exposes multiple logical IIO channels over one parent IIO channel selected through a mux-control provider.

## Important APIs, Types, And Functions
`struct mux` holds parent channel, mux control, child channel specs, ext_info wrappers, per-child cached ext_info values, cached state, and settle delay. `iio_mux_select()` selects the physical mux state, restores writable ext_info for the child if changing state, and updates cache. `mux_read_raw()`, `mux_read_avail()`, and `mux_write_raw()` forward IIO operations to the selected parent channel. `mux_read_ext_info()` and `mux_write_ext_info()` wrap parent ext_info. `mux_probe()` parses `channels`, optional `settle-time-us`, allocates a packed private area, configures child channels, and registers the IIO device.

## Control Flow
Probe gets the `"parent"` IIO channel and mux control, reads child labels, skips empty labels, copies parent channel capabilities/ext_info, validates state count against mux control states, and registers. Each read/write selects the desired state, forwards to the parent, then deselects.

## State And Persistence
`cached_state` avoids unnecessary ext_info restoration. Writable ext_info values are cached per child in devm memory so configuration follows logical channel selection. No nonvolatile state.

## Dependencies And Integration Points
Uses IIO consumer APIs, mux consumer framework, platform/OF compatible `"io-channel-mux"`, and device properties.

## Risks And Test Signals
Risks include missing locking around concurrent select/forward/deselect operations and ext_info cache lifetime/size. Test multiple children, empty channel labels, settle delays, parent scale/raw availability propagation, writable ext_info isolation per child, invalid state counts, and concurrent sysfs access.
