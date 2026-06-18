# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_kms.c

Purpose: Despite the name, this file performs low-level QXL device initialization and teardown: PCI BAR mapping, ROM validation, TTM initialization, RAM header/ring setup, memslot programming, and final cleanup.

Important APIs, types, and functions: `qxl_device_init()`, `qxl_device_fini()`, `qxl_reinit_memslots()`, `qxl_check_device()`, `setup_slot()`, `setup_hw_slot()`, and the GC work function.

Control flow: Init stores DRM drvdata, initializes mutexes/GEM, records BAR bases, creates write-combining mappings for VRAM and surface RAM, ioremaps ROM, validates ROM magic and device info, initializes BO/TTM, maps the RAM header, creates command/cursor/release ring wrappers over RAM header ring storage, initializes release and surface IDRs/locks, resets the device, installs IRQs, programs main and surface memslots, and initializes GC work. Fini releases current release BOs, asks host to free resources, waits briefly for release count to drain, flushes GC work, evicts surfaces and VRAM, finalizes GEM/TTM, frees rings/mappings, and unmaps ROM/RAM.

State and persistence: Initializes nearly all persistent `qxl_device` fields: resource bases/sizes, mappings, ROM/RAM pointers, ring wrappers, IDRs, locks, memslot metadata, and work structs. Host-visible device state is reset during init and partially rebuilt during resume through memslot reinitialization.

Dependencies and integration points: Called by PCI probe/release in `qxl_drv.c`; depends on PCI BAR layout, io_mapping, ioremap_wc, QXL protocol ROM/RAM layout, TTM/object init, IRQ init, command helpers, and memslot high-bit address encoding.

Risks: BAR selection for surface RAM falls back from 64-bit BAR 4 to 32-bit BAR 1; mapping failures must clean up in exact reverse order. `gc_work.func` is used as an initialization-complete guard. Fini waits only one second for release count to drain before eviction, so delayed host completion can expose cleanup races.

Test signals: Probe on QXL devices with 64-bit and 32-bit surface BARs; invalid ROM magic; forced mapping/ring allocation failures; suspend/resume memslot rebuild; unload with outstanding releases; TTM debugfs memory manager visibility.
