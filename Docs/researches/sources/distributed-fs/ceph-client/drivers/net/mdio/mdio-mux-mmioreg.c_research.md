<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-mmioreg.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-mmioreg.c

Purpose: simple memory-mapped register MDIO mux driver, typically for FPGA or glue registers.

Important APIs/types/functions: `struct mdio_mux_mmioreg_state` stores mux handle, physical address, register size, and mask. Key functions are `mdio_mux_mmioreg_switch_fn`, probe, and remove.

Control flow: probe obtains the MMIO resource, validates register width is 8/16/32 bits, reads `mux-mask`, verifies child `reg` values do not set unmasked bits, and calls `mdio_mux_init`. The switch function maps the register on each switch, reads current value, replaces masked bits with desired child, writes if changed, and unmaps.

State and persistence: hardware mux bits persist in the device register while powered. Driver state is the resource metadata and mux handle.

Dependencies/integration: depends on OF MDIO, HAS_IOMEM, mdio-mux core, platform bus, and phylib.

Risks and test signals: risks include repeated ioremap per switch, mask validation edge cases, concurrent external register modification, and only 8/16/32-bit width support. Tests should cover each register width, bad masks, child reg validation, same-child no-op, and parent bus deferral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-mmioreg.c -->
