## sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54usb.h

Purpose: this header defines the USB-specific protocol, hardware constants, transfer headers, register access packets, endpoint IDs, firmware upload header, and private state for `p54usb.c`.

Important types and constants: NET2280 PCI/GPIO/register macros describe the bridge setup path for version 1 devices. `struct net2280_tx_hdr` and `struct lm87_tx_hdr` are transport headers prepended before p54 frames. `enum net2280_op_type`, `struct net2280_reg_write`, and `struct net2280_reg_read` encode register transactions over bridge/device bulk endpoints. `struct x2_header` supports ISL3887 firmware upload. `enum p54u_pipe_addr` names data, management, bridge, device, and interrupt pipes. `enum p54u_hw_type` distinguishes invalid, NET2280, and 3887 hardware. `struct p54u_priv` embeds `struct p54_common` and adds USB, firmware, queue, anchor, and completion state.

Control flow and state: no functions live here, but the fields control the driver lifecycle: `upload_fw` selects the boot path, `rx_queue` and `submitted` manage URB lifetime, `fw` persists the requested firmware, and `fw_wait_load` synchronizes disconnect with the async firmware callback.

Dependencies and integration: it includes `p54pci.h` for ISL3886 register definitions and `<linux/usb/net2280.h>` for bridge bit positions. It is tightly coupled to `p54usb.c`, `p54_common`, USB URBs, and firmware loader behavior.

Risks and tests: packed struct layout and endian fields are hardware ABI. Incorrect pipe numbers, header sizes, or register constants can break firmware upload or data transfer. Build tests should catch missing definitions; runtime tests should verify endpoint detection, both TX header formats, reset/resume, and successful p54 common registration.
