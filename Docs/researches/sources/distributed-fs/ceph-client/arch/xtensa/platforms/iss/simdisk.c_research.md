# sources/distributed-fs/ceph-client/arch/xtensa/platforms/iss/simdisk.c

Purpose: Implements ISS simulated block disks backed by host files accessed through simcalls.

Important APIs, types, and functions: `struct simdisk`, module params `simdisk_count` and `filename`, `simdisk_transfer()`, `simdisk_submit_bio()`, `simdisk_open()`, `simdisk_release()`, `simdisk_attach()`, `simdisk_detach()`, proc read/write handlers, `simdisk_setup()`, `simdisk_init()`, and `simdisk_exit()`.

Control flow: Module init registers major 240, clamps disk count, allocates devices, creates `/proc/simdisk`, creates `gendisk`s, and attaches configured host files. BIO submission iterates segments, maps each bvec locally, and calls `simdisk_transfer()` to lseek/read/write host file sectors. Proc writes detach current file and attach a new one when not in use.

State and persistence: Per-disk state tracks filename, host fd, capacity, users, spinlock, gendisk, and proc entry. Host file contents persist outside the simulator.

Dependencies and integration: Block layer `submit_bio`, procfs, module params, bvec local mapping, ISS simcall file operations, and static major alias.

Risks: Transfer silently returns on beyond-end without failing the BIO; partial host I/O loops until bytes consumed but only checks `-1`; proc attach/detach is blocked by open users; host file size determines capacity.

Test signals: Create/read/write filesystem on simdisk, proc attach/detach, concurrent opens blocking detach, beyond-end I/O, host file open failure, and module unload cleanup.
