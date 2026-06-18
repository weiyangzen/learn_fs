# sources/distributed-fs/ceph-client/lib/crypto/mpi/mpi-internal.h

## Purpose
Defines private MPI types, macros, prototypes, thresholds, and architecture arithmetic bindings shared by the MPI implementation.

## Important APIs, Types, and Functions
- Defines `mpi_ptr_t`, signed `mpi_size_t`, `KARATSUBA_THRESHOLD`, `RESIZE_IF_NEEDED()`, copy/zero/normalize macros, and `UDIV_QRNND_PREINV()`.
- Declares allocation utilities, low-level limb helpers, division helpers, multiplication/Karatsuba helpers, and shift helpers.
- Supplies `longlong.h` type aliases and includes `mpi-inline.h` for GCC.

## Control Flow and State
The header is mostly declarative. The main executable macro is `UDIV_QRNND_PREINV()`, which estimates quotient/remainder using a precomputed divisor inverse, corrects overestimation, and writes outputs.

## Dependencies and Integration Points
Every MPI C file includes this header. It integrates with `<linux/mpi.h>`, kernel allocation/logging APIs, and `longlong.h`.

## Risks and Test Signals
Macros can evaluate arguments multiple times or depend on signed `mpi_size_t` behavior. `assert()` only logs and does not abort. Tests should focus on full MPI arithmetic, threshold boundary sizes around `KARATSUBA_THRESHOLD`, and division with pre-inverted divisor paths when enabled by timing macros.
