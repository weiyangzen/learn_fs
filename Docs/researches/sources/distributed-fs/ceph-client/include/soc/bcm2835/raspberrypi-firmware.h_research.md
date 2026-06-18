# sources/distributed-fs/ceph-client/include/soc/bcm2835/raspberrypi-firmware.h

Purpose: declares the Raspberry Pi firmware property mailbox interface, property tags, clock IDs, request structs, and optional firmware client APIs.

Important APIs and types: `enum rpi_firmware_property_status` defines request/success/error statuses. `struct rpi_firmware_property_tag_header` describes tag, buffer size, and request/response size. `enum rpi_firmware_property_tag` enumerates board, memory, power, clock, voltage, temperature, GPIO, framebuffer, VCHIQ, DMA, reboot, XHCI, display, OTP, and other mailbox tags. `enum rpi_firmware_clk_id` identifies firmware clocks. `struct rpi_firmware_clk_rate_request` and `RPI_FIRMWARE_CLK_RATE_REQUEST()` encode little-endian clock-rate messages. APIs include `rpi_firmware_property()`, property-list calls, get/put/devm_get, node discovery, and clock max-rate helper, with `-ENOSYS`/NULL/`UINT_MAX` stubs when disabled.

Control flow: drivers obtain a firmware handle, build tag payloads or tag lists, call the firmware property API, interpret status/returned little-endian fields, and release the handle.

State and persistence: firmware state lives on the VideoCore/firmware side and may affect clocks, power domains, framebuffer, OTP, and board state. Kernel state is handle lifetime only.

Dependencies and integration points: depends on OF device nodes, device-managed resources, endian helpers from includers, and mailbox firmware driver support. Integrates clocks, power, framebuffer, USB, GPIO, thermal, and board-info drivers.

Risks and test signals: risks include wrong payload length/alignment, endian conversion mistakes, using stubs as valid firmware, firmware tag compatibility, and mutating persistent OTP/power state unexpectedly. Test property single/list calls, disabled-config stubs, clock rate/max queries, board revision/MAC reads, framebuffer tags, power-domain changes, and error-status propagation.
