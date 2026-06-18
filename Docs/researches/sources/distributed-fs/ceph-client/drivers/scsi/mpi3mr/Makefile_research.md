# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/Makefile

## Purpose
This Makefile describes how the Broadcom MPI3MR SCSI driver is built from its implementation objects and connected to `CONFIG_SCSI_MPI3MR`.

## Important APIs, Types, And Functions
`obj-$(CONFIG_SCSI_MPI3MR) += mpi3mr.o` makes `mpi3mr.o` part of the kernel or module build when the Kconfig symbol is enabled. `mpi3mr-y` lists the component objects linked into that composite object: `mpi3mr_os.o`, `mpi3mr_fw.o`, `mpi3mr_app.o`, and `mpi3mr_transport.o`.

## Control Flow
During kbuild, the value of `CONFIG_SCSI_MPI3MR` determines whether `mpi3mr.o` is built. The `mpi3mr-y` variable tells kbuild to first compile the OS-facing, firmware, application/control, and transport portions, then link them into the single driver object.

## State And Persistence
The Makefile has no runtime state. Its persistent effect is build graph membership: the same object composition is used every time the driver is enabled until the source tree changes.

## Dependencies And Integration Points
The file integrates with the SCSI driver's Kconfig symbol and kbuild composite-object conventions. It assumes the listed source files exist in the same directory and are responsible for consuming the MPI headers under `mpi/`.

## Risks And Edge Cases
Adding a new source file without updating `mpi3mr-y` would compile cleanly only if no referenced symbols are needed, but new functionality would be absent. Renaming one of the four listed implementation files requires this Makefile to change in lockstep. Because the build is a single composite object, duplicate global symbols across the component files surface at final driver link time.

## Test Signals
Useful checks are `CONFIG_SCSI_MPI3MR=m` module builds, `CONFIG_SCSI_MPI3MR=y` built-in builds, clean incremental rebuilds after touching each component source, and link validation that all symbols used across OS, firmware, app, and transport components resolve into `mpi3mr.o`.
