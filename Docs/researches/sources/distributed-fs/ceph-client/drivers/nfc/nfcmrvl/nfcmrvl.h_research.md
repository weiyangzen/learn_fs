# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/nfcmrvl.h

Purpose: Central header for the Marvell NFC NCI driver, defining common state, platform data, transport operations, constants, and exported core functions.

Important APIs and types: Defines flags `NFCMRVL_NCI_RUNNING` and `NFCMRVL_PHY_ERROR`; coexistence/configuration ids; HCI mux constants; `enum nfcmrvl_phy`; `struct nfcmrvl_platform_data`; `struct nfcmrvl_private`; and `struct nfcmrvl_if_ops`. It declares common registration, receive, reset/halt, and DT parsing functions.

Control flow: The header establishes the transport/core split. Bus drivers fill `nfcmrvl_if_ops` and call `nfcmrvl_nci_register_dev()`. The common core later calls the same ops for open, close, send, and firmware-download transport reconfiguration.

State and persistence: `nfcmrvl_private` is the per-device runtime anchor. It persists only for the device lifetime and contains platform configuration, NCI parent, firmware download context, and PHY-private data.

Dependencies and integration points: Includes `fw_dnld.h`, depends on NFC/NCI types through users, and is consumed by all Marvell bus modules.

Risks: The header couples all transports to the firmware downloader layout. Missing or wrong `nci_update_config()` behavior can break post-firmware bus speeds. Flag bit meanings must remain synchronized with transport error handling. Test signals include building USB/UART/I2C/SPI modules and exercising common function prototypes from each transport.
