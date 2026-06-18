# sources/distributed-fs/ceph-client/drivers/message/fusion/Makefile Research

## Purpose
This Makefile maps Fusion MPT transport/control Kconfig symbols to object files.

## Important APIs, Types, And Functions
Rules build `mptbase.o`, `mptscsih.o`, and a transport object for `FUSION_SPI`, `FUSION_FC`, or `FUSION_SAS`; optional modules are `mptctl.o` for `FUSION_CTL` and `mptlan.o` for `FUSION_LAN`. A commented `ccflags-y := -DMPT_DEBUG_VERBOSE` notes an additional verbose build-time debug option.

## Control Flow
There is no runtime logic. Kbuild evaluates object lists according to selected symbols and links common/transport components into the appropriate modules or built-in objects.

## State And Persistence
The file only affects build artifacts. Debug verbosity can be changed by editing the commented `ccflags-y`, while normal logging support is controlled by Kconfig.

## Dependencies And Integration Points
It integrates the Fusion source files with Kbuild and relies on `fusion/Kconfig` to prevent invalid symbol combinations. Common objects are shared by multiple transport drivers.

## Risks
Selecting multiple Fusion transports can require careful module composition because the same common object names appear in several `obj-*` lines. Accidental enabling of the commented verbose flag would increase log volume. The Makefile has no direct rule for headers such as `lsi/mpi.h`; header compatibility is enforced only through dependent C compilation.

## Test Signals
Build SPI-only, FC-only, SAS-only, all transports, ioctl, and LAN combinations as modules and built-ins; inspect resulting modules for duplicate symbol/link errors.
