# sources/distributed-fs/ceph-client/drivers/nubus/nubus.c

## Purpose
Scans Macintosh NuBus slots, reads card ROMs through bytelane-aware accessors, parses board and functional sResource directories, populates kernel NuBus resource structures, optionally mirrors resources into procfs, and registers board devices with the NuBus bus.

## Important APIs, Types, And Functions
- `nubus_get_rom()`, `nubus_advance()`, `nubus_rewind()`, and `nubus_move()` implement bytelane-aware ROM traversal.
- `nubus_dirptr()`, `nubus_get_rsrc_mem()`, `nubus_get_rsrc_str()`, and `nubus_seq_write_rsrc_mem()` read resource data blocks/strings.
- `nubus_get_root_dir()`, `nubus_get_board_dir()`, `nubus_get_func_dir()`, `nubus_get_subdir()`, `nubus_readdir()`, and `nubus_find_rsrc()` expose directory traversal to other NuBus code and drivers.
- `nubus_first_rsrc_or_null()` / `nubus_next_rsrc_or_null()` iterate the global functional resource list.
- `nubus_get_board_resource()` and `nubus_get_functional_resource()` parse the board and function resource directories.
- `nubus_probe_slot()` detects valid format block bytelanes; `nubus_add_board()` builds board state; `nubus_scan_bus()` scans slots 9 through 14.

## Control Flow
`subsys_initcall(nubus_init)` exits unless running on Macintosh hardware. It initializes procfs, registers the parent `nubus` device, and scans slots. Slot probing checks possible bytelanes at the end of each slot address space using `hwreg_present()` and the mirrored nybble format-block marker. A valid slot is parsed by rewinding to the format block, reading ROM metadata, computing the directory pointer from signed 24-bit offset data, parsing the first board resource, then parsing remaining functional resources.

Functional resource parsing fills category/type/software/hardware ids, names, driver directory information, memory offset/length, flags, and private resources for display/network/CPU categories. Valid resources are inserted in ascending ID order into `nubus_func_rsrcs`. The completed board is registered as a device.

## State And Persistence
Global state includes `nubus_populate_procfs`, `LIST_HEAD(nubus_func_rsrcs)`, and the static parent device. Allocated `struct nubus_board` and `struct nubus_rsrc` objects persist until device release. Procfs resource trees are optional and disabled by default through the `nubus.populate_procfs` module parameter.

## Dependencies And Integration Points
Depends on Macintosh architecture setup (`MACH_IS_MAC`), fixed NuBus slot address space assumptions, `hwreg_present()`, `linux/nubus.h` resource ids, proc helper functions, and `nubus_device_register()` from `bus.c`. Exported directory/resource helpers are used by NuBus drivers.

## Risks And Edge Cases
- ROM traversal must respect bytelanes; incorrect mask handling reads bogus resources.
- Pointer movement logs when it leaves slot address space but does not hard fail.
- Many allocations use atomic context during init; failures skip resources or boards.
- Resource order sanity check drops duplicate or non-ascending functional resource ids.
- Procfs population can be expensive for some ROMs and is disabled by default.
- The code assumes classic Macintosh NuBus physical address layout.

## Test Signals
On supported Macintosh hardware, boot logs should show NuBus slot scanning and resource debug output. `/proc/nubus` should list boards, and `/proc/bus/nubus/devices` should list functional resources. Driver resource lookup through exported helpers should find expected category/type ids.
