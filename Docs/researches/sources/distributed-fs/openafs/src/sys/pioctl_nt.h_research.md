# sources/distributed-fs/openafs/src/sys/pioctl_nt.h

## Purpose
`pioctl_nt.h` declares the Windows pioctl interface and the Windows-local `ViceIoctl` block shape.

## Important APIs, types, and functions
It defines `struct ViceIoctl`/`viceIoctl_t` with `in_size`, `out_size`, `in`, and `out` fields, includes NT errno mappings, and declares `pioctl` and `pioctl_utf8`.

## Control flow
There is no runtime control flow; this header supplies the ABI used by Windows callers and `pioctl_nt.c`.

## State and persistence behavior
No state is stored here. The structure describes caller-owned in/out buffers passed to cache-manager pioctls.

## Dependencies and integration points
It depends on `afs_int32` definitions from surrounding OpenAFS headers and `afs/errmap_nt.h`. Windows tools include it to call the pioctl implementation.

## Risks
The use of `long` for sizes ties ABI assumptions to Windows compiler data models. Callers must keep buffers alive and correctly sized.

## Test signals
Compile all Windows pioctl consumers and run ANSI/UTF-8 pioctl calls with zero, input-only, output-only, and bidirectional buffers.
