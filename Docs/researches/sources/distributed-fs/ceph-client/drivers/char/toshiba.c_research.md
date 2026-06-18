# sources/distributed-fs/ceph-client/drivers/char/toshiba.c

## Purpose
`toshiba.c` is a legacy Toshiba laptop System Management Mode driver. It exposes `/dev/toshiba` for `TOSH_SMM` ioctl calls, provides `/proc/toshiba` status when procfs is enabled, probes BIOS/SMM support, and emulates fan operations on specific old models.

## Important APIs, Types, and Functions
- `tosh_smm(SMMRegisters *regs)` is exported and enters SMM by loading register values and executing an `inb $0xb2` SMM trigger, then writes register results back.
- `tosh_ioctl()` accepts `TOSH_SMM`, copies `SMMRegisters` from/to userspace, blocks HCI calls that read/write memory or PCI devices beyond allowed function range, optionally emulates fan operations, and serializes with `tosh_mutex`.
- `tosh_emulate_fan()` handles fan status/on/off for Portage 610CT and Tecra 700CS/CDT using raw ports.
- `tosh_probe()` maps BIOS ROM, checks the `TOSHIBA` signature, calls an SCI support SMM function, extracts SCI version, machine ID, BIOS version, and date, and sets fan emulation state.
- `tosh_get_machine_id()` handles both simple BIOS IDs and the special SCTTable path.
- `tosh_set_fn_port()` maps machine IDs to Fn status ports.
- `proc_toshiba_show()` emits driver format version, machine ID, SCI/BIOS versions, BIOS date, and Fn key status.

## Control Flow
Module init probes for a supported Toshiba laptop. On success it logs the version, chooses an Fn status port if not provided by module parameter, registers a fixed-minor misc device, and optionally creates `/proc/toshiba`. User ioctl calls are validated, serialized, optionally handled by fan emulation, or passed to `tosh_smm()`. Module exit removes procfs and deregisters the misc device.

## State and Persistence
Software state stores detected machine ID, BIOS version/date, SCI version, Fn port, and fan emulation flag. SMM calls and raw port fan operations can mutate persistent firmware/platform state depending on command. No driver-managed persistent storage is used.

## Dependencies and Integration Points
The driver depends on x86 BIOS ROM mapping, inline assembly SMM entry, raw I/O port access, misc core, procfs/seq_file, `linux/toshiba.h` ioctl structures, and model-specific BIOS/SMM conventions.

## Risks
- The file itself warns SMM calls can render systems unusable; user-provided register calls are only partially filtered.
- Raw BIOS parsing and port access are highly model-specific.
- `tosh_smm()` inline assembly is architecture-specific and exported to other kernel code.
- Fn/fan ports are not reserved because they overlap keyboard/PIC ranges, so conflicts are possible by design.
- `/dev/toshiba` ioctl access policy depends on device-node permissions rather than capability checks.

## Test Signals
Tests should cover probe rejection on missing signature or failed SCI support, correct machine/BIOS/proc output on known ROM images, ioctl copy error handling, filtering of dangerous HCI function ranges, fan emulation for IDs `0xfccb` and `0xfccc`, fixed misc registration, and cleanup of proc/device nodes.
