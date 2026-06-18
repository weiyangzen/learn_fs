## sources/distributed-fs/ceph-client/drivers/mtd/devices/docg3.c

Purpose: platform MTD NAND driver for M-Systems/SanDisk DiskOnChip G3 devices. It reverse-engineers ASIC register sequences, two-plane page addressing, OOB/ECC layout, bad-block table loading, erase/write/read_oob operations, DPS protection keys, debugfs views, and suspend/resume for cascaded floors.

Important APIs, types, and functions: `docg3_probe()` maps IO space, creates a `docg3_cascade`, initializes BCH, probes up to four floors, registers MTD partitions, and sysfs/debugfs. `doc_probe_device()` identifies chip IDs and fills `mtd_info` through `doc_set_driver_info()`. Core flash paths include `doc_read_oob()`, `doc_write_oob()`, `doc_erase()`, `doc_block_isbad()`, `doc_read_page_prepare()`, `doc_write_page()`, and `doc_ecc_bch_fix_data()`. Sysfs DPS helpers expose key status and key insertion.

Control flow: read paths select the floor, reset the ASIC, seek both planes, start hardware ECC, stream data/OOB through the data area, collect hardware BCH syndrome bytes, optionally correct data using the kernel BCH library, finish the page, and reset selection to floor 0. Write paths can cache OOB for a later data write or write data plus OOB in one page operation, optionally filling Hamming/BCH OOB bytes from hardware. Erase validates block alignment and erases paired plane blocks.

State and persistence: `docg3_cascade` owns shared IO base, BCH control, floor array, and a mutex serializing all hardware access. Each `docg3` stores floor id, reliable-mode setting, maximum block, BBT cache, and a one-page OOB staging buffer. Media state includes NAND data, OOB/ECC, protection areas, and bad-block metadata.

Dependencies and integration points: depends on platform resources or DT compatible `m-systems,diskonchip-g3`, MTD partition parsers `cmdlinepart` and `saftlpart`, BCH and bitrev libraries, debugfs, sysfs, tracepoints defined in `docg3.h`, and the MTD NAND OOB layout API.

Risks: comments note no public specification and unknown timings; many flows rely on observed NOP delays. `doc_probe_device()` allocates the BBT before `max_block` is set, which deserves scrutiny. OOB staging is explicitly unsafe for concurrent applications that split OOB and data writes. Suspend can fail if a floor refuses powerdown. Reliable mode changes size and erase geometry.

Test signals: floor detection, chip-id inverse check, BBT load, read_oob with corrected and uncorrectable ECC stats, raw versus auto/place OOB modes, page writes with hardware ECC OOB fill, erase paired planes, DPS sysfs key paths, debugfs register views, suspend/resume, and tracepoint visibility for register IO.
