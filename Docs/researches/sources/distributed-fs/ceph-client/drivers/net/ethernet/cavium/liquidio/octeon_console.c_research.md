# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_console.c

## Purpose
Implements host access to Octeon bootloader and PCI console memory, including named bootmem lookup, console polling, bootloader command submission, U-Boot version capture, and firmware image download/boot.

## Important APIs, Types, and Functions
Public functions are `octeon_console_send_cmd`, `octeon_wait_for_bootloader`, `octeon_init_consoles`, `octeon_add_console`, `octeon_remove_consoles`, and `octeon_download_firmware`. Internal structures mirror Octeon bootmem and console descriptors: `cvmx_bootmem_desc`, `octeon_pci_console`, and `octeon_pci_console_desc`. Important helpers include `__cvmx_bootmem_desc_get`, `CVMX_BOOTMEM_NAMED_GET_NAME`, `__cvmx_bootmem_check_version`, `cvmx_bootmem_phy_named_block_find`, `octeon_named_block_find`, `check_console`, `output_console_line`, `octeon_console_read`, and `octeon_get_uboot_version`.

## Control Flow
Console initialization verifies DDR memory access, finds the `__pci_console` named block, maps it through BAR1 static mapping, reads the number of consoles, and caches the descriptor address. Adding a console reads its ring buffer addresses and size, fetches U-Boot version by redirecting stdout to PCI, starts delayed polling, optionally enables debug console output, and marks it active. Polling reads available output bytes from a firmware ring buffer, advances the remote read index, prints complete lines while preserving leftovers, and reschedules itself. Firmware download validates the `liquidio_image.h` header, writes each image to Octeon memory in 4 MiB chunks, appends host UTC boot time to the boot command, and submits that command through the bootloader mailbox.

## State and Persistence Behavior
State is cached in `oct->bootmem_desc_addr`, `oct->bootmem_named_block_desc`, `oct->console_desc_addr`, `oct->num_consoles`, `oct->console[]`, and `oct->console_nb_info`. Console ring indices live in Octeon memory and are updated by host reads. Firmware version and boot command state are copied from the firmware header and then reflected in `oct->fw_info`.

## Dependencies and Integration Points
Depends on PCI core memory access helpers from `octeon_mem_ops.h`, indirect memory checks from `octeon_device.c`, BAR1 setup callbacks in `oct->fn_list`, CRC32, delayed work, and the firmware image layout from `liquidio_image.h`. It is used by PF firmware loading and diagnostics rather than the VF-only probe path.

## Risks
The remote lock functions are placeholders, so concurrent console or bootmem access is not serialized beyond caller behavior. Ring index validation prevents obvious out-of-range reads, but firmware-provided descriptor addresses and sizes are trusted after named block discovery. `octeon_download_firmware` validates the header but relies on the caller-provided `size` for the initial minimum only; image payload lengths should be covered by higher-level firmware loading tests. Polling uses a static console buffer shared by invocations.

## Test Signals
Bootloader readiness timeout, command length rejection, console named block missing, bootmem version mismatch, console ring wraparound, partial-line leftover printing, add/remove console with delayed work cancellation, U-Boot version capture, valid firmware boot, invalid firmware magic/CRC/version/image count, large image chunk writes, and boot command buffer overflow checks are key signals.
