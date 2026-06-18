# File Research: sources/block-storage/util-linux/sys-utils/lscpu-dmi.c

`lscpu-dmi.c` decodes selected SMBIOS/DMI table data for aarch64 CPU reporting and socket counting.

Key behavior:
- Converts raw SMBIOS bytes into `struct lscpu_dmi_header`.
- Resolves SMBIOS string indices with `dmi_string()`.
- `parse_dmi_table()` walks DMI structures and extracts BIOS vendor, system manufacturer/product, and processor information.
- For processor records, it captures manufacturer, version, current/max speed, part number, processor family, and increments socket count.
- `dmi_decode_cputype()` reads `/sys/firmware/dmi/tables/DMI`, parses it, and populates BIOS CPU vendor/model/family fields.
- `get_number_of_physical_sockets_from_dmi()` returns the number of processor records found.

Important dependencies:
- `get_mem_chunk()` from `lscpu-virt.c`.
- DMI path `_PATH_SYS_DMI` from `lscpu.h`.

Risk notes:
- `parse_dmi_table()` uses `st.st_size / 4` as a synthetic structure count when callers do not know the true DMI count.
- Some field reads use raw casts to `uint16_t *`, so behavior assumes the platform tolerates unaligned little-endian SMBIOS reads.
- If DMI data is malformed, parsing stops and callers usually fall back silently.
