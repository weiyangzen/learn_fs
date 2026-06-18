# sources/distributed-fs/openafs/src/vol/voldefs.h

## Purpose
Defines fundamental volume type constants, volume-group limits, partition limits, on-disk volume header filename formats, and server metadata paths for the OpenAFS volume package.

## Important APIs, Types, and Functions
Volume type aliases map historic names to numeric constants: `RWVOL`, `ROVOL`, `BACKVOL`, and `RWREPL`, with `VOLMAXTYPES` set to 4. `VOL_VG_MAX_VOLS` caps volume group members handled together at 20. `VOL_MAX_CHECKOUT_RETRIES` caps retry loops when checkout/locking races with fileserver restart. `VOLMAXPARTS` is 255.

`VFORMATDIGITS`, `VHDREXT`, `VFORMAT`, and `VHDRNAMELEN` define the `V0000000000.vol` or legacy `.vl` header filename contract. `VMAXPATHLEN` caps external volume path names. Namei builds define `INODEDIR` as `AFSIDat`. `MAXVOLIDPATH` and `SERVERLISTPATH` point to server-wide volume id and server id metadata.

## Control Flow
No executable control flow exists here. These constants steer parsing, allocation, retry, and filename generation in the volume package. In this subset, `vol-salvage.c` uses `VOL_VG_MAX_VOLS`, `VOL_MAX_CHECKOUT_RETRIES`, `VOLMAXPARTS`, `VFORMAT`, `VHDRNAMELEN`-related naming behavior, `VMAXPATHLEN`, and volume type constants.

## State and Persistence Behavior
The filename macros are persistent ABI: changing `VHDREXT` or `VFORMAT` changes the names used for on-disk volume header files and must match all readers/writers. The volume type constants are stored in volume metadata and interpreted by fileserver, volserver, and tooling.

## Dependencies and Integration Points
Requires `<afs/param.h>` before filename macros so `AFS_VOLID_FMT` is available. Integrates with `volume.h`, salvager, vutil, namei storage, max volume id allocation, and server identity configuration.

## Risks
The comments explicitly warn that changing volume types requires checking `volumeWriteable` and that `VHDREXT` and `VFORMAT` must change together. `VOL_VG_MAX_VOLS` bounds DAFS VG query handling; exceeding it would require protocol and allocation changes.

## Test Signals
Header filename round-trip tests, volume creation/deletion, salvager volume-header scanning, and platform builds for AIX/HPUX versus normal `.vol` naming validate this file. Retry behavior around fileserver restarts exercises `VOL_MAX_CHECKOUT_RETRIES`.

## Source Notes
Read as C header; 93 source lines; source-tree-aligned report generated for subset `subset-b-007819`.
