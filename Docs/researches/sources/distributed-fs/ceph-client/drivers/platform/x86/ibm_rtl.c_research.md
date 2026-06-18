# sources/distributed-fs/ceph-client/drivers/platform/x86/ibm_rtl.c

Purpose: IBM Premium Real Time Mode driver. It finds an `_RTL_` table in the BIOS EBDA and exposes sysfs controls to enter or exit PRTM/real-time mode by issuing the firmware-described I/O or MMIO command.

Important APIs/types/functions: `struct ibm_rtl_table` maps the packed firmware table. `ibm_rtl_init()` checks DMI/EFI, maps EBDA, scans for the signature, maps the command port, and creates a system bus. `ibm_rtl_write()` writes enter/exit commands, triggers the firmware port write with width 8/16/32, waits for completion, and checks `command_status`. Sysfs attributes are `version` and writable `state`.

Control flow: init optionally honors `force`, otherwise rejects EFI boot and non-IBM DMI systems, maps EBDA first to read size then fully, scans word-aligned offsets for `_RTL_`, reads command metadata, maps command address as I/O or MMIO, and registers sysfs. Writing `state` with `0` or `1` calls `ibm_rtl_write()`. Exit forces state `0`, tears down sysfs, and unmaps memory/ports.

State and persistence: globals hold mapped EBDA/table/command address and command type/width. Hardware mode can persist beyond process lifetime, so module exit explicitly exits PRTM.

Dependencies and integration: DMI, EFI detection, BIOS EBDA helper, ioport/ioremap accessors, sysfs bus registration, mutex serialization, and non-atomic 64-bit I/O helper for signature reads.

Risks: direct EBDA scanning and firmware command execution are platform-sensitive. `rtl_port_unmap()` calls `ioport_unmap()` when the address is NULL and command type is not MMIO, so failure cleanup deserves scrutiny. Test signals include forced load, no EBDA, malformed table, MMIO vs I/O command mapping, command timeout/status failures, sysfs permissions, and exit restoring non-PRTM state.
