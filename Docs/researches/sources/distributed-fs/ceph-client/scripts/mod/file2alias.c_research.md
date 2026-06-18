<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/file2alias.c -->
# sources/distributed-fs/ceph-client/scripts/mod/file2alias.c

## Purpose

`file2alias.c` converts `MODULE_DEVICE_TABLE()` ELF symbols into generated `MODULE_ALIAS()` metadata. It decodes target-compiled device-id arrays for many buses and appends alias strings to the module record used by `modpost`.

## Important APIs, Types, and Functions

The public entry point is `handle_moddevtable()`. Core helpers include `module_alias_printf()`, `do_table()`, `sym_is()`, `add_uuid()`, `add_guid()`, and many `do_*_entry()` handlers for USB, OF, HID, PCI, ACPI, PNP, input, virtio, vmbus, I2C, SPI, DMI, platform, AMBA, CPU, Type-C, MHI, auxiliary, CDX, and other buses. `struct devtable` maps device-table names to target sizes and handler callbacks.

## Control Flow

For each ELF symbol, `handle_moddevtable()` filters for section-relative object symbols named `__mod_device_table__kmod_<modname>__<type>__<name>`. It obtains symbol data from the ELF image or zero-fills NOBITS data, finds the matching `devtable` entry, checks array size and NULL terminator, and invokes the bus-specific entry formatter for each element except the terminator. Handlers read fields through generated offsets and `get_unaligned_native()`, construct modalias syntax, and deduplicate aliases.

## State and Persistence Behavior

State is appended to `mod->aliases` as dynamically allocated `struct module_alias` entries. Built-in aliases may carry a builtin module name later emitted by `modpost`; loadable modules become `MODULE_ALIAS()` lines in generated `.mod.c`.

## Dependencies and Integration Points

It depends on target ELF definitions from `elfconfig.h`, offsets from `devicetable-offsets.h`, `linux/mod_devicetable.h`, `modpost.h`, list helpers, and `xalloc`. It is linked into host `modpost` and feeds module autoloading through depmod/modalias consumers.

## Risks and Edge Cases

The file is sensitive to device-table layout, target endianness, unaligned access, alias grammar, and terminator validation. A missing or wrong handler breaks device autoloading. Fixed-size alias buffers and string formatting require careful bounds assumptions. Composite match rules such as USB BCD ranges and input bitmaps are easy to regress.

## Test Signals

Compile test modules with every `MODULE_DEVICE_TABLE()` family and compare generated aliases against expected modalias strings. Test malformed arrays, missing terminators, NOBITS all-zero tables, duplicate aliases, cross-endian builds, and new bus table additions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/file2alias.c -->
