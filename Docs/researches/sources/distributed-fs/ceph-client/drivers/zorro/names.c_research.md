<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/names.c -->
# sources/distributed-fs/ceph-client/drivers/zorro/names.c

## Purpose
`names.c` resolves Zorro manufacturer/product IDs into human-readable device names during initialization.

## Important APIs, types, and functions
Key private types are `struct zorro_prod_info` and `struct zorro_manuf_info`. The exported init helper is `zorro_name_device`. It includes generated `devlist.h` three times to create initdata strings, product arrays, and manufacturer arrays.

## Control flow
`zorro_name_device` searches manufacturers by `ZORRO_MANUF(dev->id)`, then products by combined product/EPC value. It leaves the generic name if no manufacturer matches, writes a manufacturer-only fallback if product is unknown, and appends `(#n)` for repeated products.

## State and persistence
The lookup tables and strings are `__initdata` and discarded after boot. `seen` counters track duplicate naming during initialization.

## Dependencies and integration points
It depends on `devlist.h`, Zorro ID macros, and `struct zorro_dev`. It is called from Zorro bus enumeration before device registration/resources are published.

## Risks and test signals
Risks include generated table mismatches, duplicate counter mutation in initdata, and name buffer overflow if generated names exceed expected sizes. Test signals include known/unknown manufacturer/product devices, duplicates, and `CONFIG_ZORRO_NAMES=n` fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/zorro/names.c -->
