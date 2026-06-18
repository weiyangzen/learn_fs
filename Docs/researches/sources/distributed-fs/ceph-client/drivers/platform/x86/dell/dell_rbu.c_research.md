## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell_rbu.c

Purpose: legacy Dell Remote BIOS Update driver. It creates a platform device with binary sysfs attributes that let userspace stage a BIOS image in memory for firmware to consume after reboot. It supports monolithic (`mono`) and packetized (`packet`) modes, plus `init` to recreate firmware loader entries.

Important APIs/types/functions: global `rbu_data` tracks mono buffer, packet list, sizes, read cursor, and spinlock. `struct packet_data` represents one packet with allocated pages. `img_update_realloc()` allocates contiguous DMA32 pages for mono images. `packetize_data()` and `create_packet()` allocate packet pages above `allocation_floor`, mark them uncached with `set_memory_uc()`, copy image chunks, and append to `packet_data_list`. `packet_read_list()` and `read_packet_data()` expose staged packet data through `data` bin attribute. `callbackfn_rbu()` receives firmware from `request_firmware_nowait()`.

Control flow: module init registers platform device `dell_rbu` and sysfs binary attributes `data`, `image_type`, and `packet_size`. Users set image type and packet size, then trigger firmware loading externally. Firmware callback fills mono or packet storage. Reads expose the staged image. Changing image type or packet size frees previous allocations.

State and persistence: all staged BIOS image bytes live in kernel memory until freed, overwritten, or module exit. Cleanup zeroes image/packet memory before freeing and restores packet memory writeback caching. Firmware update itself depends on external userspace setting CMOS/reboot state, not this driver alone.

Dependencies and integration: platform device/sysfs binary attributes, firmware loader, page allocator, DMA32 allocation, spinlocks, list API, `set_memory_uc/wb`, and Dell BIOS update conventions.

Risks: large allocations can fail or fragment memory. Packet allocation loops can allocate temporary below-floor pages. `image_type_write()` modifies the sysfs write buffer in place and uses substring matching. Some paths return raw or confusing errors. Test signals include mono and packet staging/readback, packet size validation, allocation-floor behavior, memory zeroing on mode switch/exit, firmware callback with zero size, and concurrent sysfs access under spinlock.
