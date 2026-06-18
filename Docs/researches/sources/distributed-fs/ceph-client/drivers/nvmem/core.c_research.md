<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/core.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/core.c

## Purpose
Implements the NVMEM framework core: provider registration, consumer lookup, cell parsing, sysfs access, fixed/layout cell creation, keepout handling, notifier events, and exported read/write helpers.

## Important APIs, Types, And Functions
Internal types are `struct nvmem_cell_entry` and `struct nvmem_cell`. Provider APIs include `nvmem_register()`, `devm_nvmem_register()`, `nvmem_unregister()`, `nvmem_add_one_cell()`, notifier registration, and layout registration. Consumer APIs include `nvmem_device_get()/put()`, `devm_nvmem_device_get()/put()`, `nvmem_cell_get()/put()`, `of_nvmem_cell_get()`, `nvmem_cell_read()/write()`, typed reads, variable-length little-endian reads, device direct reads/writes, and lookup table add/delete.

## Control Flow
Providers register with `nvmem_config`; the core allocates ids, initializes a bus device, obtains optional write-protect GPIO, copies config fields, validates keepouts, adds static and DT cells, registers the device, populates layouts, creates sysfs cell files, and emits notifiers. Consumers first try OF phandle lookup, then platform lookup tables. Cell reads call provider `reg_read`, apply bit shifting, invoke optional post-processing, and return allocated buffers. Writes validate read-only state and bit-cell sizing, merge unaffected bits from hardware when needed, toggle write-protect GPIO around provider writes, and return byte counts.

## State And Persistence
Framework state includes the global NVMEM bus, ida ids, provider refcounts, cell lists, lookup list, blocking notifier chain, optional sysfs attributes, and per-device layout pointer. Hardware persistence is delegated to providers; the core only mediates access and stores metadata.

## Dependencies And Integration Points
Integrates with Linux driver core, sysfs, OF phandles, GPIO descriptors, module refcounts, NVMEM provider/consumer public headers, layout bus helpers, and devres. It is initialized by `subsys_initcall()` so providers and consumers can bind early.

## Risks
Lifetime and locking are central: cells reference provider entries, consumers hold module and kref references, and layout modules may need extra references before generated cells exist. Bit-cell write preparation reads adjacent hardware bits, so volatile or write-once backing stores need caution. Keepout ranges must be sorted and word/stride aligned. Sysfs `force_ro` can change writeability when a provider has `reg_write`.

## Test Signals
Exercise provider registration/unregistration, devm cleanup, OF cell lookup, lookup-table fallback, fixed layout and dynamic layout cells, sysfs raw and cell reads, write-protect GPIO toggling, read-only enforcement, keepout fill behavior, bit-offset cell reads/writes, typed reads, and module unload with live consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/core.c -->
