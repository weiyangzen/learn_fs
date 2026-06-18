<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/xway_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/xway_nand.c

Purpose: Lantiq XWAY raw parallel NAND controller driver. It maps the SoC EBU NAND window, wires legacy `nand_chip` byte/command callbacks, configures the EBU chip-select/timing registers, scans one NAND chip, and registers the resulting MTD device.

Important APIs/types/functions: `struct xway_nand_data` owns `nand_controller`, `nand_chip`, saved EBU lock flags, and the MMIO NAND address. `xway_readb()`/`xway_writeb()` perform address-bit-based data, command, and address accesses. `xway_select_chip()` gates `EBU_NAND_CON` and serializes with global `ebu_lock`. `xway_cmd_ctrl()` emits CLE/ALE cycles and polls `NAND_WAIT_WR_C`. `xway_dev_ready()` returns `NAND_WAIT_RD`. `xway_attach_chip()` defaults unknown software ECC to Hamming. Probe/remove are `xway_nand_probe()` and `xway_nand_remove()`.

Control flow: platform probe allocates state, ioremaps resource 0, sets the DT flash node and parent device, installs legacy NAND callbacks, initializes the controller, reads optional `lantiq,cs`, programs `EBU_ADDSEL1`, `LTQ_EBU_BUSCON1`, and `EBU_NAND_CON`, sets default software ECC, calls `nand_scan(&chip, 1)`, then `mtd_device_register()`. Command flow is core raw-NAND -> legacy callbacks -> EBU address-bit strobes -> ready polling.

State and persistence: Persistent state is on NAND only; runtime state is EBU register configuration, the MTD registration, and NAND core bad-block/ECC state. The driver takes and releases `ebu_lock` around chip select to protect shared EBU register programming. Remove unregisters the MTD and calls `nand_cleanup()`.

Dependencies/integration: Depends on `linux/mtd/rawnand.h`, platform devices, OF, and Lantiq `lantiq_soc.h` helpers (`ltq_ebu_w32`, `ltq_ebu_w32_mask`, `ltq_ebu_r32`, `ebu_lock`). Integrates with device tree compatible `lantiq,nand-xway`, the raw NAND core, and normal MTD partition registration.

Risks: Busy-wait polling has no timeout in `xway_cmd_ctrl()`, so a wedged EBU can hang the caller. Only chip selects -1 and 0 are supported; unexpected selects call `BUG()`. The read buffer uses `NAND_WRITE_DATA` as the offset, which equals the read data path by macro value but is easy to misread. ECC defaults are conservative but may not match all attached boards.

Test signals: Boot a DT system with `lantiq,nand-xway`, verify EBU register setup, successful `nand_scan`, MTD registration, bad-block scan, read/write/erase through `mtd-utils`, and software Hamming ECC behavior. Compile-test coverage should include raw NAND API changes and Lantiq platform declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/xway_nand.c -->
