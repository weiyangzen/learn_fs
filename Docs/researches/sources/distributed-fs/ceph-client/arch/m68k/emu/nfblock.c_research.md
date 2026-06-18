# sources/distributed-fs/ceph-client/arch/m68k/emu/nfblock.c

Purpose: ARAnyM NatFeat block driver exposing XHDI disks as Linux block devices.

Important APIs and data: `nfhd_read_write()`, `nfhd_get_capacity()`, `struct nfhd_device`, `nfhd_submit_bio()`, `nfhd_getgeo()`, `nfhd_ops`, `nfhd_init_one()`, `nfhd_init()`, and `nfhd_exit()`. `major_num` is a module parameter.

Control flow and state: init obtains NatFeat ID `XHDI`, registers a block major, scans emulated device IDs 8-23, queries capacity, allocates `nfhd_device` plus `gendisk`, sets capacity, adds disks, and links devices on `nfhd_list`. Bio submission iterates segments and calls XHDI read/write with physical segment addresses, then completes the bio. Exit removes disks and unregisters the major.

Dependencies and integration: NatFeat base, Linux block layer, bio physical address mapping, and ARAnyM XHDI ABI. Runtime state is the device list, gendisks, major number, and emulator-backed disk contents.

Risks and test signals: `nfhd_submit_bio()` ignores emulator read/write return errors and still ends I/O successfully. Segment length/sector shifting depends on power-of-two block size. Test disk scan, invalid block size rejection, read/write data integrity, error injection if emulator supports it, and unload cleanup.
