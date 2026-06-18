# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/fw_dnld.h

Purpose: Defines the firmware-image ABI and runtime state used by the Marvell firmware downloader.

Important APIs and types: Constants include `NFCMRVL_FW_MAGIC`, proprietary boot command ids, logical connection ids, helper packet formats, and retry flags. Packed structs describe per-PHY boot settings: `nfcmrvl_fw_uart_config`, `nfcmrvl_fw_i2c_config`, `nfcmrvl_fw_spi_config`, `nfcmrvl_fw_binary_config`, and the top-level `nfcmrvl_fw` header. `struct nfcmrvl_fw_dnld` stores the active firmware download session. Function prototypes expose init/deinit/start/abort and frame receive hooks to `main.c`.

Control flow: The header has no executable flow, but it fixes the data contract consumed by `fw_dnld.c`: a firmware blob starts with `struct nfcmrvl_fw`, then offsets select bootrom, helper, and firmware payload/config regions.

State and persistence: Runtime state includes firmware name, `struct firmware` ownership, parsed header/config pointers, state/substate, offset/chunk tracking, a single-thread RX workqueue, SKB queue, and timer. The packed firmware header is a persistent on-disk ABI.

Dependencies and integration points: Includes workqueue types and forward-declares `struct nfcmrvl_private`; it is included by `nfcmrvl.h`, so most Marvell transport files see the downloader state.

Risks: Packed layout and endianness must match firmware-generation tooling. `union` members expose typed config views over raw bytes, so bad offsets or wrong PHY ids produce unsafe transport settings. Test signals are compile coverage of all PHY builds plus firmware-download tests for UART/I2C/SPI binary configs.
