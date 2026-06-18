# sources/distributed-fs/ceph-client/drivers/comedi/comedi_internal.h

## Purpose

`comedi_internal.h` is the private header shared by COMEDI core files. It exposes internal cross-file declarations without making them public kernel APIs.

## APIs And Flow

It forward-declares COMEDI core structs and declares range ioctl handling, board/subdevice minor allocation and free, hardware-device release, buffer allocation/reset/map helpers, internal buffer reservation helpers, scan-progress and event helpers, device cancel/detach/attach functions, subdevice private auto-free helpers, default buffer-size globals, COMEDI driver list globals, and `insn_inval()`. With `CONFIG_PROC_FS` disabled, proc init/cleanup are inline no-ops.

## State, Dependencies, Risks, Tests

The header owns no direct state, but declares persistent globals such as default buffer sizes and the driver list lock. It depends on compiler/types headers and forward declarations. Risks are stale prototypes, accidental exposure of private helpers, missing optional stubs, and mismatched locking expectations. Test COMEDI builds with and without `PROC_FS`, sparse/prototype warnings, and no external users of the private header.
