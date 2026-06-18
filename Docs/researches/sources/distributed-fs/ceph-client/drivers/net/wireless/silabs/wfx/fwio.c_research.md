# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/fwio.c

Purpose: Implements secure firmware loading and early hardware initialization for WF200 devices.

Important APIs and functions: `wfx_init_device()` configures direct access/byte order/reset, validates config register/device ID, initializes IGPR values, wakes the WLAN CPU, releases reset, loads firmware, and enables data IRQs. Firmware helpers include `get_firmware()`, `wait_ncp_status()`, `upload_firmware()`, `load_firmware_secure()`, `wfx_sram_write_dma_safe()`, `print_boot_status()`, and `init_gpr()`.

Control flow and integration: Probe calls this before normal IRQ subscription. Secure loading handshakes through DCA SRAM registers: host ready, read bootloader/PTE keyset, load matching `*.sec` firmware, write signature/hash/version/image size, stream 1 KiB blocks into the download FIFO with PUT/GET flow control, wait for authentication, and signal jump. After boot, common probe polls for the startup HIF indication.

State and persistence: Stores `wdev->keyset` from firmware metadata. Firmware image state is pushed into device SRAM/DCA registers; GPR config persists in chip until reset.

Dependencies: Depends on Linux firmware loader, hex parsing, HWIO SRAM/AHB/register helpers, PDS/firmware filenames from platform data, and WF200 boot ROM DCA status constants.

Risks and test signals: Risks include incompatible keyset selection, vmalloc firmware data used for DMA without bounce, FIFO flow-control timeout, firmware size misalignment, boot-status ambiguity, byte-order/direct-access mistakes, and development hardware wake timeout. Tests should cover keyset-specific and fallback firmware names, corrupted KEYSET header, wrong keyset, DMA bounce path, DCA timeouts, auth fail errors, SPI/SDIO boot, and startup indication after load.

Test signals: Source read size: 389 lines, 11444 bytes.
