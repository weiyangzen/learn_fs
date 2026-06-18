# sources/distributed-fs/ceph-client/tools/cgroup/iocost_coef_gen.py

Purpose: Generates blk-iocost linear cost model coefficients by running destructive or file-backed fio benchmarks and printing a line suitable for `/sys/fs/cgroup/io.cost.model`.

Important APIs, types, and functions: `dir_to_dev()` maps a path to whole block device and major:minor. `create_testfile()` creates a direct-IO test file, attempts `chattr +C`, and fills it from `/dev/urandom` through `pv` and `dd`. `run_fio()` runs fio with JSON output and returns aggregate bandwidth. `restore_elevator_nomerges()` restores scheduler and merge settings.

Control flow: Parses benchmark parameters, validates required commands, chooses raw block device or file target, records current scheduler and `nomerges`, disables scheduler/merges, runs six fio workloads for sequential bandwidth and 4K sequential/random IOPS in read/write directions, restores settings, and prints `MAJ:MIN rbps=...`.

State and persistence: Can write a large test file in the current directory. It writes `/sys/block/<dev>/queue/scheduler` and `nomerges` and registers an `atexit` restoration handler. Raw `--testdev` writes to the whole device and is destructive.

Dependencies and integration points: Requires fio, findmnt, pv, dd, sysfs block queue controls, and root-level permissions for raw devices/sysfs. Output integrates with cgroup v2 io.cost.model.

Risks: Shell command construction uses paths directly and assumes trusted arguments. Raw device mode can destroy data. If the process is killed with SIGKILL, scheduler/nomerges may not restore. The fio JSON parser assumes job read/write keys and bandwidth fields exist.

Test signals: Use a loop device or disposable block device, short durations, quiet/verbose modes, missing command detection, existing correctly-sized testfile reuse, and restoration after exceptions.
