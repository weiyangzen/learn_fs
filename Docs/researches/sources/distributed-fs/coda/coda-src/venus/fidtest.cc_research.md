# sources/distributed-fs/coda/coda-src/venus/fidtest.cc

## Purpose
This small diagnostic program calls the Venus pioctl interface to print the Coda Fid, realm, and version vector for a path.

## Important APIs, Types, and Functions
`GetFid` mirrors the expected `VIOC_GETFID` output: `ViceFid`, `ViceVersionVector`, and realm string. `main()` prepares a `ViceIoctl`, calls `pioctl(argv[1], VIOC_GETFID, ...)`, prints `FID_(&out.fid)` and the realm, then prints version vector sites, store id, and flags.

## Control Flow
The program zeroes output storage, invokes pioctl on the first command-line argument, exits with failure on error, and prints fields on success.

## State and Persistence Behavior
It reads kernel/Venus state only and does not persist or mutate filesystem data.

## Dependencies and Integration Points
It depends on `venusioctl.h`, `vice.h`, `pioctl`, `FID_`, and the Venus kernel/user pioctl contract.

## Risks and Test Signals
Risks include no argc validation before `argv[1]`, legacy `void main`, and fixed output struct compatibility with the pioctl implementation. Tests should call it with a valid Coda path, a non-Coda path, no argument, and paths from multiple realms.
