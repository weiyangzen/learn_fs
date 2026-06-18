# sources/distributed-fs/ceph-client/drivers/sh/intc/access.c

Purpose: low-level register accessor and mode-dispatch helpers for the SH INTC framework.

Important APIs and functions: `intc_phys_to_virt` translates physical register addresses through descriptor windows. `intc_get_reg` indexes the descriptor register table. `intc_set_field_from_handle` and `intc_get_field_from_handle` manipulate encoded bitfields. `test_8/16/32`, `write_8/16/32`, and `modify_8/16/32` implement width-specific raw access. Dispatch tables `intc_reg_fns`, `intc_enable_fns`, `intc_disable_fns`, and `intc_enable_noprio_fns` map encoded handle function/mode fields to runtime operations.

Control flow: higher-level handle code encodes register index, mode, width, and shift into a handle. IRQ chip operations later decode the handle and call these dispatch tables to enable, disable, acknowledge, test, or set priority fields.

State and dependencies: state is descriptor register/window arrays; accessor functions themselves are stateless. Dependencies include raw MMIO and `internals.h` handle macros. Risks include `BUG()` on missing register mapping, local IRQ masking around read-modify-write only on the local CPU, write-posting flush assumptions, and invalid width-to-dispatch encoding. Test signals include enable/disable bit changes on real INTC registers, priority field updates, ack writes, and boot without `BUG()` from descriptor table mismatches.
