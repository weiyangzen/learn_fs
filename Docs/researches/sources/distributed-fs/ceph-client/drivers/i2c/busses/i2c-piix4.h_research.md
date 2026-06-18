
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-piix4.h

Purpose: this header defines the register-offset macros and exported helper prototypes shared by the PIIX4/SB800 SMBus implementation and any companion code needing controlled SB800 port selection or transactions.

Important APIs, types, and functions: the `SMBHSTSTS`, `SMBHSLVSTS`, `SMBHSTCNT`, `SMBHSTCMD`, `SMBHSTADD`, `SMBHSTDAT0`, `SMBHSTDAT1`, `SMBBLKDAT`, `SMBSLVCNT`, `SMBSHDWCMD`, `SMBSLVEVT`, and `SMBSLVDAT` macros derive I/O port addresses from a local variable named `piix4_smba`. `PIIX4_BLOCK_DATA` defines the encoded controller operation for SMBus block transfers. `struct sb800_mmio_cfg` carries an optional mapped FCH MMIO pointer and a `use_mmio` selector. Function declarations expose `piix4_sb800_port_sel()`, `piix4_transaction()`, `piix4_sb800_region_request()`, and `piix4_sb800_region_release()`.

Control flow: there is no executable control flow in the header, but the macro design intentionally requires callers to have a `piix4_smba` variable in scope. The region request/release prototypes define the expected bracket around SB800 indexed or MMIO access, while `piix4_sb800_port_sel()` is used to change and restore multiplexed SMBus port state around a transaction.

State and persistence: `struct sb800_mmio_cfg` is transient per caller and points to mapped MMIO only while the region is held. The macros do not store state; they compute port addresses for inb/outb operations.

Dependencies and integration points: it includes `linux/types.h` and expects Linux `struct device` and `struct i2c_adapter` declarations through including translation units. The helper functions are exported from `i2c-piix4.c` in the `PIIX4_SMBUS` namespace.

Risks: macro dependence on an in-scope `piix4_smba` name is easy to misuse and cannot be type-checked. Callers must pair region request/release and restore previous SB800 port selection. The header exposes low-level register operations, so misuse can collide with firmware or other controllers.

Test signals: build coverage for all including files, namespace symbol resolution, sparse/compiler warnings around missing declarations, and runtime tests that region request/release and port selection are paired correctly by users.
