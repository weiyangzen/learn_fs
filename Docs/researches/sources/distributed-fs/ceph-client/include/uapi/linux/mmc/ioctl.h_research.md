# sources/distributed-fs/ceph-client/include/uapi/linux/mmc/ioctl.h

## Purpose
Defines MMC block-device ioctl ABI for issuing raw MMC commands and bounded multi-command sequences from userspace.

## Important APIs, Types, And Functions
Exports `mmc_ioc_cmd`, `mmc_ioc_multi_cmd`, `MMC_IOC_CMD`, `MMC_IOC_MULTI_CMD`, `MMC_IOC_MAX_BYTES`, `MMC_IOC_MAX_CMDS`, and helper macro `mmc_ioc_cmd_set_data`.

## Control Flow
Userspace fills opcode, argument, flags, block size/count, timeouts, direction, optional reliable-write bit, and `data_ptr`; the driver sends the command and writes response words back. Multi-command ioctl executes `cmds[]` in sequence.

## State, Persistence, And Dependencies
Command effects persist on the card depending on opcode, especially RPMB or write commands. Dependencies are `linux/types.h` and `linux/major.h`.

## Integration Points
Used by eMMC/SD provisioning, RPMB tooling, diagnostics, and card-management utilities on MMC block devices.

## Risks
Raw commands can corrupt media. `data_ptr` alignment and 32/64-bit ABI padding are critical. The ioctl enforces per-call byte and command-count limits; larger transfers must use normal block I/O.

## Test Signals
Validate struct size on 32/64-bit builds, read-command response/data, multi-command ordering, max byte/count rejection, reliable-write flag handling, and timeout overrides.
