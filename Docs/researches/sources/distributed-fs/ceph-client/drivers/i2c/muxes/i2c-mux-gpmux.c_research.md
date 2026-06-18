# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-mux-gpmux.c

Purpose: generic-purpose I2C mux using the kernel mux-control subsystem instead of direct GPIO/register control.

Important APIs/types: `struct mux` stores a `struct mux_control *` and a `do_not_deselect` flag. Select/deselect callbacks are `i2c_mux_select()` and `i2c_mux_deselect()`.

Control flow: probe requires OF, gets an unnamed mux control, resolves `i2c-parent`, counts child nodes, allocates a mux core, honors optional `mux-locked`, and for each child validates `reg` against `mux_control_states()` before adding a child adapter. Select calls `mux_control_select()`, recording whether deselect should be skipped after a failed select. Deselect calls `mux_control_deselect()` unless select failed.

State and persistence: selected mux-control state lives in the mux subsystem/hardware. Driver state stores the parent adapter reference, child adapters, and `do_not_deselect` error guard.

Dependencies and integration: depends on OF, mux consumer API, platform driver core, and I2C mux core.

Risks: invalid child `reg` values can exceed mux-control states. Failed select leaves deselect intentionally skipped, so hardware may remain in its previous state. Parent adapter references must be released on all failure paths.

Test signals: child state validation, mux-control select/deselect calls, `mux-locked` behavior, failed select handling, adapter cleanup on bad child nodes, and remove cleanup.
