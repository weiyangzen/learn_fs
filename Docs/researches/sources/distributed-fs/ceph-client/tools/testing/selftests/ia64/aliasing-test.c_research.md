# sources/distributed-fs/ceph-client/tools/testing/selftests/ia64/aliasing-test.c

Purpose: this IA-64-oriented selftest exercises historically troublesome `/dev/mem`, PCI legacy memory, PCI ROM, and `/proc/bus/pci` mmap/read paths. The goal is not that every range be readable; the goal is that mapping or reading failures are handled without machine checks or inaccessible-device failures.

Important APIs and functions: `map_mem()` opens a path, optionally issues `PCIIOC_MMAP_IS_MEM` for `/proc/bus/pci/*`, mmaps a requested range, optionally touches every int in the mapping into global `sum`, unmaps, and returns 0 for success, positive for not mappable, and negative for access/setup errors. `scan_tree()` recursively finds matching files and applies `map_mem()`. `read_rom()` enables a sysfs ROM by writing `"1"` and reads it into `buf`. `scan_rom()` recursively finds `rom` files and invokes `read_rom()`. `main()` orchestrates fixed `/dev/mem` ranges and recursive scans.

Control flow: `main()` tests low memory ranges separately, treats whole-1MiB mapping as allowed to fail positively, scans `/sys/class/pci_bus` `legacy_mem`, scans `/sys/devices` `rom`, then scans `/proc/bus/pci` function names matching `??.?`. Recursive walkers allocate child paths, skip `.`/`..`, branch on filename matches, and OR return codes into a cumulative result.

State and persistence: global `sum` prevents read-touch loops from being optimized away; `buf` holds ROM chunks. The test does not write persistent files, but it writes to sysfs ROM enable files and opens/mmap device memory.

Dependencies and integration points: uses libc directory, mmap, stat, fnmatch, and PCI ioctl APIs; depends on `/dev/mem`, sysfs PCI legacy memory/ROM files, `/proc/bus/pci`, and permissions suitable for raw memory access.

Risks: `map_mem()` leaks `fd` if `mmap()` fails; pointer arithmetic on `void *` is a GNU extension; some recursive error paths return before freeing all allocated entries; `read_rom()` writes two bytes (`"1"` including NUL) to a sysfs attribute. The test is inherently platform/permission sensitive and can be dangerous outside its intended hardware/kernel context.

Test signals: stderr prints `PASS` for readable, mappable, not mappable, or unreadable ROM cases that do not represent access failure, and `FAIL` for inaccessible paths. Exit status is based on the whole `/dev/mem` 1MiB mapping result, so log review is important for recursive scan failures.
