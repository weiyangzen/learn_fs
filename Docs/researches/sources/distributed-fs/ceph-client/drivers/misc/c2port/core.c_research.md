# sources/distributed-fs/ceph-client/drivers/misc/c2port/core.c

## Purpose
`c2port/core.c` implements the generic Silicon Labs C2 programming class. It bit-bangs the C2 protocol through backend-provided GPIO/I/O operations and exposes device identification and flash read/write/erase controls through sysfs.

## Important APIs, Types, and Functions
Exported APIs are `c2port_device_register()` and `c2port_device_unregister()`. Low-level protocol helpers include `c2port_reset()`, `c2port_strobe_ck()`, `c2port_write_ar()`, `c2port_read_ar()`, `c2port_write_dr()`, `c2port_read_dr()`, `c2port_poll_in_busy()`, and `c2port_poll_out_ready()`. Sysfs attributes cover `name`, `flash_blocks_num`, `flash_block_size`, `flash_size`, `access`, `reset`, `dev_id`, `rev_id`, `flash_access`, `flash_erase`, and binary `flash_data`.

## Control Flow
Backends register a `struct c2port_device` with line-control ops and flash geometry. The core allocates an ID, creates `c2portN` under a class whose dev_groups expose the sysfs API, and disables access by default. Users must enable `access`, optionally enable `flash_access` through the two-key FPCTL sequence, then use `flash_data` reads/writes or `flash_erase`. Flash block operations select `C2PORT_FPDAT`, send a command, poll busy/ready status, check `C2PORT_COMMAND_OK`, transfer address/length bytes, and then stream up to 128 bytes per sysfs binary operation.

## State and Persistence
Global state is the C2 class and IDR. Per-device state includes ID, name, backend ops, mutex, access flag, flash access flag, and device object. Flash writes/erases persist in the target microcontroller; driver state itself is volatile.

## Dependencies and Integration Points
The core depends on `linux/c2port.h`, class/device/sysfs infrastructure, IDR, delays, local IRQ disabling for sub-5us C2 timing, and backend callbacks for `access`, `c2d_dir`, `c2d_get`, `c2d_set`, and `c2ck_set`.

## Risks and Edge Cases
The C2 bit timings use `udelay()` and local IRQ disabling but are still sensitive to CPU/platform behavior. Sysfs flash writes can permanently alter target firmware and are guarded only by `access`/`flash_access`. Addressing sends only high/low bytes, so large flash geometries would need review. Some comments note missing status checks before access sequences. `devdata` is accepted by `c2port_device_register()` but not stored.

## Test Signals
Validate class creation/destruction, ID allocation/removal, sysfs permission and gating behavior, device/revision reads, flash-access enable sequence, erase arming sequence, 128-byte chunk boundaries, offset at end-of-flash, backend timeout handling, and concurrent sysfs access serialization by the per-device mutex.
