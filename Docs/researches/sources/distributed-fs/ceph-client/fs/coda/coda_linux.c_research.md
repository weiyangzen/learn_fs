# sources/distributed-fs/ceph-client/fs/coda/coda_linux.c

## Purpose
`coda_linux.c` provides Linux-specific helper conversions for Coda: fid formatting, control-name recognition, open-flag translation, time conversion, inode type mapping, and VFS/Coda attribute translation.

## Important APIs, Types, And Functions
Public functions are `coda_f2s()`, `coda_iscontrol()`, `coda_flags_to_cflags()`, `coda_inode_type()`, `coda_vattr_to_iattr()`, and `coda_iattr_to_vattr()`. It also defines global `coda_fake_statfs`.

## Control Flow
Open flags are converted into Coda `C_O_*` flags. Venus `coda_vattr` values are copied into Linux inode fields only when not set to sentinel `-1`; Linux `iattr` valid bits are converted back into Coda attributes with unspecified fields initialized to sentinel values.

## State, Persistence, And Dependencies
The only global is the fake statfs flag. All conversion state is on-stack or in caller-provided inode/attribute structures. Dependencies include Linux credentials/user namespace conversions, VFS inode timestamps, and Coda UAPI attributes.

## Integration Points
`cnode.c` uses attribute-to-inode conversion during inode fill; setattr paths use inode-to-Coda conversion before Venus upcalls; file open/release maps Linux flags to Venus flags; directory lookup recognizes `.CONTROL`.

## Risks
`coda_f2s()` uses a static buffer and is not reentrant. UID/GID conversion assumes `init_user_ns`. Sentinel handling must stay aligned with Venus protocol expectations, especially for timestamps and sizes.

## Test Signals
Test all open flag combinations, `.CONTROL` matching, vattr sentinel handling, uid/gid/mode/size/time translation, static fid formatting in logs, and setattr round trips.
