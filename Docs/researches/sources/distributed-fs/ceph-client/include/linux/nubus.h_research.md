
# sources/distributed-fs/ceph-client/include/linux/nubus.h

Purpose: declares the classic Macintosh NuBus resource, board, driver, procfs, and device-model interfaces.

Important APIs/types/functions: `struct nubus_dir`, `nubus_dirent`, `nubus_board`, and `nubus_rsrc` model ROM directories, resources, boards, slots, categories, types, and driver data. `struct nubus_driver` provides match/probe/remove. Iteration macros walk global and per-board resources. Directory APIs get root/board/function directories, read or find resources, rewind, get subdirectories, copy resource memory, and emit seq_file output. Device/driver APIs register NuBus devices and drivers and provide drvdata helpers. `nubus_slot_addr()` maps slot numbers to physical slot address space.

Control flow: platform NuBus discovery populates boards and function resources, optional procfs exposes resource data, drivers register a `nubus_driver`, match resources, probe boards, and store private data on the board device.

State and persistence: state is boot/discovery-time hardware inventory in lists and device model objects. Resource ROM data is hardware-provided and read-only; procfs entries are derived views.

Dependencies and integration points: depends on device model, list heads, procfs, seq_file, and architecture slot address mapping. It integrates m68k Macintosh bus discovery, legacy drivers, and optional procfs diagnostics.

Risks and test signals: risks include malformed ROM directory parsing, bad slot address calculations, driver/resource lifetime mismatches, and procfs stubs hiding missing diagnostics. Test signals include NuBus enumeration on supported m68k configs, resource iterator coverage, procfs dump validation, driver register/unregister tests, and invalid directory entry fuzzing where feasible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nubus.h -->
