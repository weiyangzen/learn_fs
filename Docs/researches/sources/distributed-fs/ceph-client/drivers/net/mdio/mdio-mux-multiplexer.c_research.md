<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-multiplexer.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-multiplexer.c

Purpose: MDIO mux driver using the generic kernel mux consumer subsystem for child selection.

Important APIs/types/functions: `struct mdio_mux_multiplexer_state` stores a `mux_control`, whether a deselect is needed, and mux handle. Core routines are `mdio_mux_multiplexer_switch_fn`, probe, and remove.

Control flow: probe obtains the mux control, stores state, and initializes mdio-mux children. The switch function no-ops when already selected, otherwise deselects the previous mux state when required, selects the desired child through `mux_control_select`, and records whether a later deselect is needed. Remove uninitializes child buses and deselects if selected.

State and persistence: runtime state is the mux subsystem's selected state, `do_deselect`, and child bus registrations.

Dependencies/integration: depends on OF MDIO, mdio-mux core, `MULTIPLEXER`, mux consumer API, and platform bus. Compatible string is `mdio-mux-multiplexer`.

Risks and test signals: risks include deselect/select ordering, mux provider failures while under MDIO locks, stale `do_deselect`, and parent-bus deferral. Tests should cover failed deselect/select, repeated same child, remove after selection, and mux provider probe deferral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-multiplexer.c -->
