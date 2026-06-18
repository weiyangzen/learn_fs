# sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole-coreboot.c

Purpose: Exposes the coreboot CBMEM console ring buffer as `/sys/firmware/log` through the shared memconsole infrastructure.

Important APIs/types/functions: `cbmem_cons` models the firmware console header and ring data. `memconsole_coreboot_read()` maps logical reads over either a linear buffer or wrapped ring-buffer segments. `memconsole_probe()` maps the CBMEM console and registers the shared sysfs binary file.

Control flow: On a coreboot device with tag `CB_TAG_CBMEM_CONSOLE`, probe temporarily maps the header to read size, then maps the full buffer using devm memory remap. It calls `memconsole_setup()` with the ring-buffer read function and creates sysfs via `memconsole_sysfs_init()`. Remove calls `memconsole_exit()`.

State and persistence behavior: Global `cbmem_console` and `cbmem_console_size` point at firmware-owned log memory. The log can change at runtime if firmware appends messages; the driver deliberately rereads cursor on each access.

Dependencies and integration points: Depends on coreboot table bus, memory remapping, and the shared `memconsole.c` sysfs layer.

Risks and test signals: Firmware-controlled cursor/size can race with reads; size is read once to reduce overrun risk. Test with non-wrapped and wrapped logs, concurrent firmware logging if available, short/offset sysfs reads, and module removal.
