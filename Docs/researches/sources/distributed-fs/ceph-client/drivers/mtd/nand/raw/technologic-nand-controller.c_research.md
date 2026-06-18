## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/technologic-nand-controller.c

Purpose: this is the Technologic Systems TS72xx NAND controller driver. It exposes a memory-mapped NAND bus where address-line aliases select control and busy views, and implements modern `exec_op` callbacks for command, address, data, and wait-ready operations.

Important APIs, types, and functions: `struct ts72xx_nand_data` embeds a `nand_controller`, one `nand_chip`, and three MMIO pointers: base data, control alias, and busy alias. `ts72xx_nand_attach_chip()` rejects on-host ECC and defaults software ECC to Hamming. `ts72xx_nand_ctrl()` updates CLE/ALE/NCE bits. `ts72xx_nand_exec_instr()` handles individual NAND operation instructions, and `ts72xx_nand_exec_op()` runs them in order.

Control flow: probe allocates data, initializes controller ops, maps the base resource, derives control/busy aliases by adding fixed address-line offsets, requires exactly one child NAND node, sets the flash node and MTD parent, defaults ECC to software, scans one chip, and registers MTD with parser support. Runtime operations are straightforward: command and address instructions assert the relevant control bits around byte writes, data instructions use `ioread8_rep()`/`iowrite8_rep()`, and WAITRDY polls the busy alias for bit 5.

State and persistence: driver runtime state is limited to MMIO aliases and embedded NAND objects. Persistent media state comes from the child node, generic MTD partition parsing, and software Hamming ECC selection. Remove unregisters MTD, cleans NAND, and puts the firmware node handle.

Dependencies and integration points: it uses raw NAND `exec_op`, `linux/mtd/platnand.h`, firmware child nodes, platform MMIO resources, `readb_poll_timeout()`, and the `technologic,ts7200-nand` compatible.

Risks: the address-line alias scheme assumes the platform maps enough address space for `BIT(22)` and `BIT(23)` offsets from the base mapping. The driver claims it expects exactly one child but only fetches the first child, so extra children are not explicitly rejected. `fwnode_handle_put()` in remove uses `dev_fwnode(&pdev->dev)` rather than the child handle acquired in probe, which is a lifetime area to verify. Unsupported on-host ECC returns `-EINVAL`.

Test signals: successful DT child parsing, command/address strobes on the alias control address, busy polling bit 5, byte-stream reads and writes, software Hamming correction, partition parser registration, and remove-path handle cleanup under probe failure and normal unbind.
