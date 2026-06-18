# sources/distributed-fs/ceph-client/lib/crypto/mpi/Makefile

## Purpose
Builds the kernel MPI multiprecision math library when `CONFIG_MPILIB` is enabled.

## Important APIs, Types, and Functions
- Produces `mpi.o` from `mpi-y`.
- Lists generic limb helpers, MPI public operations, coding helpers, division/multiplication internals, modular exponentiation, and utility allocation code.

## Control Flow and State
There is no runtime logic. The file controls object composition and link order for the MPI library.

## Dependencies and Integration Points
Integrated with Kbuild through `obj-$(CONFIG_MPILIB) = mpi.o`. Other crypto and public-key code depend on this library for big integer arithmetic.

## Risks and Test Signals
The risk is omission or ordering errors when adding/removing MPI source files. Build tests with `CONFIG_MPILIB=y/m`, module symbol resolution, and public-key crypto tests are the relevant signals.
