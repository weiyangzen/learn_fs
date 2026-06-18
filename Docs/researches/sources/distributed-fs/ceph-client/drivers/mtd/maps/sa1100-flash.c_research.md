# sources/distributed-fs/ceph-client/drivers/mtd/maps/sa1100-flash.c

Purpose: SA11x0 platform CFI flash map driver. It discovers one or more platform memory resources, builds one `map_info` per chip select, probes the selected map driver from `flash_platform_data->map_name`, optionally concatenates multiple banks with `mtd_concat_create()`, and registers parsed or platform partitions through `mtd_device_parse_register()`.

Important APIs/types/functions: `struct sa_subdev_info`, `struct sa_info`, `sa1100_set_vpp()`, `sa1100_probe_subdev()`, `sa1100_setup_mtd()`, `sa1100_mtd_probe()`, `sa1100_destroy()`. It depends on platform resources, `flash_platform_data`, SA1100 MSC bankwidth bits, `simple_map_init()`, `do_map_probe()`, and MTD partition parsers `"cmdlinepart"` and `"RedBoot"`.

Control flow: probe fetches platform data, allocates flexible subdevice state, calls optional platform `init()`, probes each memory resource, accepts partial success when later banks return `-ENXIO`, concatenates multiple successful banks, then registers partitions. Remove unregisters the exposed MTD, destroys concatenation if present, unmaps each bank, releases regions, frees state, and calls optional platform `exit()`.

State and persistence: persistent flash state is entirely on hardware; driver state tracks mapped windows, probed MTDs, and a global VPP refcount protected by `sa1100_vpp_lock`. VPP nesting is process-wide, so all subdevices share one programming-voltage lifetime.

Risks and test signals: VPP refcount underflow would call platform `set_vpp(0)` incorrectly; only callers following map-layer pairing keep it safe. Bankwidth inference only handles CS0/CS1 and defaults unknown bases to CS0. Tests should exercise single-bank, multi-bank concat, missing second bank, platform init failure, partition parser fallback, remove cleanup, and nested write operations that toggle VPP.
