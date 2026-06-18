# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_glue.h

## Purpose
This header defines the Linux adaptation contract for the `sym53c8xx_2` driver. It pulls in the required kernel, SCSI, PCI, and transport headers; defines Linux-specific configuration hooks and barriers; maps endian-sensitive SCRIPTS patching helpers; and declares the OS-facing state embedded in the core driver structures.

## Important APIs, Types, and Functions
Key macros include `SYM_CONF_TIMER_INTERVAL`, `SYM_OPT_LIMIT_COMMAND_REORDERING`, printk compatibility wrappers, `MEMORY_READ_BARRIER()`, `MEMORY_WRITE_BARRIER()`, `cpu_to_scr()`, `scr_to_cpu()`, `SCSI_SUCCESS`, `SCSI_FAILED`, `sym_name()`, and `sym_print_addr()`. The header explicitly rejects `SYM_CONF_CHIP_BIG_ENDIAN`; chips are supported only in little-endian addressing mode.

`struct sym_slcb` is the Linux-specific LUN extension and stores `reqtags` plus `scdev_depth`. `struct sym_shcb` is the Linux-specific host extension embedded in the HCB: unit number, instance/chip names, `Scsi_Host *`, MMIO/SRAM ioremaps, timer, last timer tick, and settle-time state. `struct sym_device` is a probe-time wrapper used before full HCB allocation, carrying `pci_dev`, bus addresses, mapped addresses, chip descriptor, NVRAM pointer, and selected host ID. `struct sym_data` is the `Scsi_Host` private data tying Linux to `struct sym_hcb`.

Inline helpers include `sym_get_hcb()` for hostdata lookup, `sym_set_cam_status()`, `sym_get_cam_status()`, and `sym_set_cam_result_ok()`. Cross-file declarations include `sym_set_cam_result_error()`, `sym_xpt_done()`, `sym_xpt_async_bus_reset()`, `sym_setup_data_and_start()`, `sym_log_bus_error()`, and `sym_dump_registers()`.

## Control Flow
The header has no runtime control flow by itself, but it determines how control flows between Linux glue and the core. `sym_glue.c` allocates `struct sym_data` as `Scsi_Host` private data and uses `sym_get_hcb()` from every callback. `sym_hipd.c` calls the declared glue functions when it completes commands, reports reset events, needs Linux result mapping, or dumps PCI/register diagnostics. Including `sym_fw.h` and `sym_hipd.h` after the Linux definitions lets the OS-neutral code compile with Linux-specific HCB/LCB extensions available.

## State and Persistence Behavior
State declared here is runtime-only. `struct sym_shcb` persists for the life of one host adapter and stores mappings and timer state. `struct sym_slcb` persists per allocated LUN while the SCSI device exists. `struct sym_data` persists for the `Scsi_Host` lifetime and is also used during PCI error recovery. No settings are written back to firmware or NVRAM by this header.

## Dependencies and Integration Points
This file is the include pivot for Linux kernel APIs, SCSI core APIs, SPI transport, local driver headers (`sym53c8xx.h`, `sym_defs.h`, `sym_misc.h`, `sym_fw.h`, and `sym_hipd.h`), and architecture I/O functions. Its barrier and endian macros are used by the SCRIPTS/core paths for DMA-visible queue ordering and script instruction patching. Its type extensions are referenced throughout `sym_glue.c`, `sym_hipd.c`, and NVRAM helpers.

## Risks
Because this header defines structure extensions that are embedded into core types, small layout or macro changes can break many source files at once. `sym_get_cam_status()` returns `host_byte(cmd->result)` while `sym_set_cam_status()` writes the host byte field directly; callers must preserve SCSI status bits correctly. The SCRIPTS endian macros assume little-endian chip addressing; adding big-endian chip mode would require a larger audit than changing the macro. Barrier macros are minimal wrappers and rely on explicit PCI dummy reads elsewhere for posted-write ordering.

## Test Signals
Useful signals include allmodconfig/build testing for the driver, sparse/endian checking around `cpu_to_scr()` and `scr_to_cpu()`, command result mapping tests through success and error completions, host reset/bus reset settle-time behavior, timer initialization and deletion, PCI error-recovery use of `struct sym_data`, and compile coverage with optional proc/NVRAM/MMIO configuration combinations.
