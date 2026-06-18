# sources/distributed-fs/ceph-client/drivers/phy/broadcom/phy-brcm-usb-init.h

Purpose: Defines the shared Broadcom USB PHY initialization contract between the platform PHY driver and chip-specific initialization library. It provides mode constants, register-bank selectors, helper macros, the ops vtable, the parameter/state carrier, and endian-aware MMIO helpers.

Important APIs and types: `USB_CTLR_MODE_HOST`, `USB_CTLR_MODE_DEVICE`, `USB_CTLR_MODE_DRD`, and `USB_CTLR_MODE_TYPEC_PD` encode controller role support. `enum brcmusb_reg_sel` indexes controller, xHCI EC/global, USB PHY, USB MDIO, and BDC EC register bases. `struct brcm_usb_init_ops` is the callback interface used by the platform driver. `struct brcm_usb_init_params` holds mapped register bases, IOC/IPP polarity, role selection, family/product IDs, selected family metadata, selector bit maps, optional PIARB syscon, and wake state. The header declares the SoC initializer functions and inlines wrappers such as `brcm_usb_init_common()` and `brcm_usb_uninit_xhci()`.

Control flow: The header has no standalone driver flow. Callers allocate/fill `brcm_usb_init_params`, call a `brcm_usb_dvr_init_*()` function to install `ops`, and then use the inline wrappers to conditionally dispatch callbacks if present. Register macros build offsets from symbolic names that are defined in the `.c` file.

State and persistence: `struct brcm_usb_init_params` is the persistent software state passed through all PHY init, exit, sysfs, suspend, and resume operations. The inline MMIO helpers perform read/modify/write operations that persist in hardware. The header itself owns no storage except constants and type definitions.

Dependencies and integration points: Includes `linux/regmap.h`; relies on Linux bit/MMIO APIs available through including translation units. The endian-aware `brcm_usb_readl()` and `brcm_usb_writel()` choose `__raw_*` on big-endian MIPS because that platform reverses bus endianness by strap, and use relaxed little-endian I/O elsewhere. It is included by both `phy-brcm-usb.c` and `phy-brcm-usb-init.c`.

Risks: The macros concatenate register and field names, so the implementation file must define exact `USB_CTRL_*` symbols before use. The ops wrappers hide missing callbacks by doing nothing, which is useful for cross-family support but can mask incomplete family bring-up. Any change to `enum brcmusb_reg_sel` order affects register-base arrays and DT resource mapping.

Test signals: Compile all Broadcom PHY variants, probe with old index-based and new named register resources, exercise init/exit paths on big-endian and little-endian platforms, and verify sysfs role selection updates `port_mode` through the ops wrappers.
