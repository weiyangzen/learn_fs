# sources/distributed-fs/ceph-client/drivers/scsi/scsi_proc.c

## Purpose

`scsi_proc.c` implements the legacy `/proc/scsi` interface. It creates `/proc/scsi/scsi` for listing attached SCSI devices and for manual add/remove commands, and it manages per-host-template proc directories and per-host proc files used by older low-level drivers for debugging, statistics, and driver-specific commands.

## Important APIs, types, and functions

`scsi_init_procfs()` and `scsi_exit_procfs()` create and remove the top-level proc entries. `scsi_proc_hostdir_add()` and `scsi_proc_hostdir_rm()` maintain one directory per `scsi_host_template` that implements `show_info`. `scsi_proc_host_add()` and `scsi_proc_host_rm()` create and remove host-number files inside that template directory. `scsi_template_proc_dir()` is exported for drivers that need the template proc directory.

The file's local state is `proc_scsi`, `global_host_template_mutex`, and `scsi_proc_list`, whose entries are `struct scsi_proc_entry` records containing the host template, proc directory, and `present` host count. Proc operations are split between host-specific files (`proc_scsi_ops`) and the global device list/control file (`scsi_scsi_proc_ops`).

## Control flow

For host-specific proc files, open uses `single_open_size()`, show delegates to `shost->hostt->show_info()`, and write copies at most `PROC_BLOCK_SIZE` bytes from user memory before calling `shost->hostt->write_info()`. Host template directory creation is reference-counted by `present`: the first host for a template creates `/proc/scsi/<proc_name>`, later hosts reuse it, and the last removal deletes it.

For `/proc/scsi/scsi`, read uses a `seq_file` iterator over `scsi_bus_type` devices, filters for SCSI device objects, and prints host/channel/id/lun plus INQUIRY vendor/model/rev/type/ANSI data. Write accepts only `scsi add-single-device H C I L` and `scsi remove-single-device H C I L`. Add looks up the host and calls a transport `user_scan()` hook or `scsi_scan_host_selected(..., SCSI_SCAN_MANUAL)`. Remove looks up the host and device and calls `scsi_remove_device()`.

## State and persistence behavior

Procfs entries persist while SCSI procfs is initialized and while host templates/hosts remain registered. The host-template list is protected by `global_host_template_mutex`. Writes to `/proc/scsi/scsi` persist by changing the live SCSI device graph: add may allocate and publish devices through the scan/sysfs path, while remove unregisters devices. The proc files themselves do not store command history.

## Dependencies and integration points

The file depends on procfs, seq_file, user-copy helpers, SCSI host/device/transport APIs, `scsi_priv.h`, and `scsi_logging.h`. It integrates with host registration in `hosts.c`, with scanning in `scsi_scan.c`, with removal in `scsi_sysfs.c`, and with low-level driver callbacks `show_info` and `write_info`. Drivers such as `esas2r` use the exported `scsi_template_proc_dir()`.

## Risks and edge cases

The interface is legacy and string-parsed. `proc_scsi_write()` uses fixed command prefixes and `simple_strtoul()` parsing, so malformed spacing or missing fields can silently become zero values before the called scan/remove path rejects or acts. Host proc writes allocate a single page and pass raw data to low-level drivers; those drivers own validation. The template directory lifetime depends on balanced hostdir add/remove calls and `present` accounting. Device iteration must correctly put references in seq start/next/stop paths; missing puts would leak devices, and extra puts would race with removal.

## Test signals

Procfs tests should verify `/proc/scsi/scsi` creation/removal, attached-device listing, manual add/remove commands, malformed command rejection, and host-template directory reference counting with multiple hosts using the same template. Driver callback tests should cover `show_info` and `write_info` paths. Concurrency tests should read the seq file while devices are added and removed and should exercise repeated host add/remove cycles.
