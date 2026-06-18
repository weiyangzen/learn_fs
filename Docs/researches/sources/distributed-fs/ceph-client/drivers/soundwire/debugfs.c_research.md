# sources/distributed-fs/ceph-client/drivers/soundwire/debugfs.c

## Purpose
Implements SoundWire debugfs support for bus and slave devices. It creates a global `soundwire` debugfs root, per-master directories, per-slave register dumps, and an unsafe command interface for arbitrary column-0 or BPT/BRA reads and writes.

## Important APIs, Types, and Functions
Exported functions are `sdw_bus_debugfs_init()`, `sdw_bus_debugfs_exit()`, `sdw_slave_debugfs_init()`, `sdw_slave_debugfs_exit()`, `sdw_debugfs_init()`, and `sdw_debugfs_exit()`. Register dump helpers include `sdw_sprintf()` and `sdw_slave_reg_show()`. Command controls are backed by `set_command()`, `set_command_type()`, `set_start_address()`, `set_num_bytes()`, `cmd_go()`, `do_bpt_sequence()`, and `read_buffer_show()`.

## Control Flow
Subsystem init creates `/sys/kernel/debug/soundwire` and a writable `firmware_file` string. Each bus creates `master-controller-link`; each slave creates a directory with `registers`, command-control files, `go`, `read_buffer`, and optional `firmware_file`. Reading `registers` resumes the slave, reads DP0, SCP, SDCA, banked, and DP1-14 registers through no-PM SoundWire reads, prints `XX` for failed reads, and releases runtime PM. For commands, users set command direction, command type, start address, byte count, and firmware file for writes, then write `1` to `go`. `cmd_go()` resumes the device, optionally loads firmware data, performs column-0 nread/nwrite or synchronous BPT, stores reads in a global buffer, logs timing, and drops the PM reference.

## State and Persistence Behavior
Global debugfs state includes `sdw_debugfs_root`, `cmd`, `cmd_type`, `start_addr`, `num_bytes`, a 1 MiB `read_buffer`, and `firmware_file`. These globals are shared by all slaves and masters, so concurrent debugfs users affect each other. Per-bus and per-slave debugfs dentries are stored in `bus->debugfs` and `slave->debugfs` and removed recursively on exit. Command operations taint the kernel with `TAINT_USER` because they mutate hardware behind normal driver state.

## Dependencies and Integration Points
Depends on `CONFIG_DEBUG_FS`, firmware loading, PM runtime, SoundWire core read/write/BPT APIs, SoundWire register definitions, and debugfs file helpers. The stubs in `bus.h` remove these hooks when debugfs is disabled. It integrates with bus/slave lifecycle through `sdw_bus_master_add/delete()` and slave add/delete paths.

## Risks
The command interface is intentionally unsafe: it can alter device registers outside driver synchronization and shares global command state across all slaves. `firmware_file` is a global string pointer exposed in each slave directory, so one user changes it for everyone. The read buffer is a large static allocation and can expose stale data if a read fails after partial completion. BPT sequence allocates a section but relies on cleanup-free style only for local pointer lifetime. Register dumps perform many bus transactions and may perturb runtime PM or timing-sensitive devices.

## Test Signals
Tests should cover debugfs root/master/slave creation and removal, register dumps on attached and inaccessible slaves, command validation for invalid direction/type/size/address, firmware write path, column-0 read/write path, BPT read/write path, read_buffer formatting, concurrent command users on two slaves, runtime PM failures, and disabled-debugfs builds using stubs.
