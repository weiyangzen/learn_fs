# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_mass_storage.c

## Purpose

`f_mass_storage.c` implements the USB composite Mass Storage Function. It exposes one or more file-backed logical units to a USB host through Bulk-Only Transport and a SCSI command emulation layer, with configfs and legacy helper entry points for gadget compositions.

## Important APIs, Types, and Functions

The central runtime object is `struct fsg_common`, which owns gadget references, EP0 state, LUN array, pipeline buffers, exception state, SCSI command state, wait queues, the backing-file semaphore, and the main kernel thread. `struct fsg_dev` is the per-USB-function endpoint wrapper. Public helper exports include `fsg_common_set_sysfs()`, `fsg_common_set_num_buffers()`, `fsg_common_set_cdev()`, `fsg_common_create_lun()`, `fsg_common_create_luns()`, `fsg_common_set_inquiry_string()`, `fsg_common_free_buffers()`, `fsg_common_remove_lun()`, `fsg_common_remove_luns()`, and `fsg_config_from_params()`.

Control requests enter through `fsg_setup()` for Bulk-Only reset and Get Max LUN. USB data movement is handled by `start_transfer()`, `start_in_transfer()`, `start_out_transfer()`, `bulk_in_complete()`, and `bulk_out_complete()`. SCSI command handling is split across `received_cbw()`, `get_next_command()`, `do_scsi_command()`, `check_command()`, `finish_reply()`, and `send_status()`. The file-backed command implementations include `do_read()`, `do_write()`, `do_verify()`, `do_synchronize_cache()`, `do_inquiry()`, `do_request_sense()`, capacity and CD-ROM helpers, mode sense/select, start-stop, prevent-allow, and format-capacity handling.

## Control Flow

`fsg_alloc_inst()` creates configfs instance state, allocates buffer heads, and creates a default removable `lun.0`. `fsg_alloc()` creates a `usb_function`. `fsg_bind()` verifies at least one LUN, attaches strings, starts the `file-storage` kernel thread if needed, allocates interface and endpoints, and assigns FS/HS/SS descriptors. `fsg_set_alt()` and `fsg_disable()` do not directly reconfigure endpoints; they raise configuration-change exceptions for the main thread. `do_set_interface()` then disables old endpoints, frees requests, enables the selected endpoints, allocates per-buffer IN/OUT requests, and marks LUN unit attention as reset.

At runtime `fsg_main_thread()` loops through CBW receive, SCSI dispatch, data reply, and CSW status. It polls for signals and raised exceptions between each phase. CBW parsing validates signature, LUN, flags, CDB length, and transfer length. SCSI commands set expected direction and byte count, check the medium and CDB fields, perform file I/O under `filesem`, then update residue and sense data. Exceptions such as protocol reset, abort bulk-out, config change, and exit cancel pending USB requests, reset buffer state, optionally clear forced halts, and complete delayed EP0 status.

## State and Persistence Behavior

Persistent device-visible state is the host-visible SCSI medium backed by files or block devices opened by `storage_common` helpers. Driver state is in-memory: LUN flags, sense data, unit attention, prevent-removal flag, CBW/CSW fields, buffer-head state, and endpoint enablement. The backing file remains open while the main thread is alive, which intentionally keeps the underlying filesystem busy. `filesem` serializes backing file changes against command execution; `lock` protects exception state and thread pointer; wait queues coordinate USB completion with the main thread.

Configfs state controls `stall`, optional debug `num_buffers`, and per-LUN `file`, `ro`, `removable`, `cdrom`, `nofua`, `inquiry_string`, and `forced_eject`. Sysfs LUN attributes are available when `fsg_common_set_sysfs()` is used. No driver settings are persisted across module or gadget teardown.

## Dependencies and Integration Points

The implementation depends on the USB composite framework, gadget endpoint APIs, configfs, kernel threads/freezer, Linux file I/O (`kernel_read`, `kernel_write`, fsync/invalidate helpers), and `storage_common.h` for LUN definitions, descriptors, SCSI constants, and attribute helpers. It registers as `DECLARE_USB_FUNCTION_INIT(mass_storage, ...)`, so configfs gadgets instantiate it as the `mass_storage` function. Legacy composite gadgets can use the exported common helpers and `fsg_config_from_params()`.

## Risks and Test Signals

Risks include races around delayed EP0 status tags, endpoint halt/wedge recovery on controllers with limited stall support, keeping backing files open during shutdown, partial read/write rounding to block size, SCSI phase-error correctness, overflow in command block counts, malformed CBW handling, and configfs LUN mutation while bound. `fsg_common_set_num_buffers()` accepts the requested count and relies on callers/configfs policy; very small or large values should be tested under debug builds.

Strong test signals include enumeration at FS/HS/SS, Get Max LUN and Bulk Reset, invalid CBW wedge and reset recovery, read/write/verify/capacity/mode-sense command sequences from Linux, Windows, and macOS hosts, removable-media eject and forced-eject behavior, read-only/CD-ROM/nofua combinations, backing-file replacement while idle versus busy, suspend/freezer interaction, bind/unbind with live transfers, and failure injection in endpoint autoconfig, request allocation, and backing-file I/O.
