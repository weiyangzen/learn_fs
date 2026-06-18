# sources/distributed-fs/ceph-client/drivers/mtd/maps/sc520cdp.c

Purpose: AMD Elan SC520 Customer Development Platform map driver. It exposes two 8 MiB 32-bit flash banks and an optional 512 KiB DIL flash, optionally reprogramming SC520 PAR registers to avoid BIOS aliasing, then concatenates the two main banks into one MTD device.

Important APIs/types/functions: `sc520cdp_map[]`, `mymtd[]`, `merged_mtd`, `sc520cdp_setup_par()`, `init_sc520cdp()`, `cleanup_sc520cdp()`, `struct sc520_par_table`, `SC520_PAR_ENTRY()`. It depends on MMCR `ioremap()`, `readl()/writel()` PAR access, `simple_map_init()`, map probes (`cfi_probe`, `jedec_probe`, `map_rom`), and `mtd_concat_create()`.

Control flow: optional PAR setup maps MMCR, finds ROMCS0/ROMCS1/BOOTCS PAR entries by target-device bits, rewrites them, or falls back to BIOS addresses. Init maps each flash window, initializes map callbacks, probes in CFI/Jedec/ROM order, records successful MTDs, concatenates banks 0 and 1 when at least two devices are found, and separately registers the third DIL flash when present. Cleanup unregisters concat/DIL devices, destroys maps, and unmaps windows.

State and persistence: runtime state is static arrays of map descriptors and MTD pointers. Reprogrammed PAR settings persist at least until platform reset and alter physical decode behavior.

Risks and test signals: `devices_found >= 2` assumes banks 0 and 1 exist, even though the count is not tied to indices. PAR programming failures silently fall back per bank. Tests should simulate missing banks, failed maps, probe fallback order, cleanup after partial discovery, and variable PAR table matches.
