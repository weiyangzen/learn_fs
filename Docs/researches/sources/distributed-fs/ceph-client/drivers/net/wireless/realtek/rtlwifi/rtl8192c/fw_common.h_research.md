# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/fw_common.h

`fw_common.h` declares firmware-size/page constants, chip-version helper macros, H2C payload setters, and exported firmware command APIs for RTL8192C-family common code.

Important constants include `FW_8192C_SIZE`, firmware start/end addresses, page size, polling delay, timeout count, and header signature detection through `IS_FW_HEADER_EXIST()`. Version macros classify normal chips, RF type, 92C serial, UMC vendor, and UMC B-cut devices. H2C setters fill power-mode, join-report, and reserved-page-location payload bytes. Prototypes expose firmware download, H2C fill, firmware self-reset, power mode, reserved pages, join report, USB async write, and P2P PS offload.

The header has no runtime control flow; its macros are consumed by `fw_common.c` and common DM/chip-specific code. Risks include signature-mask drift, version-helper mismatch, payload setters without bounds checks, and the `usb_writeN_async()` declaration requiring matching providers. Test signals are PCI/USB builds, firmware header parsing, chip-version branch coverage, and H2C command byte validation.
