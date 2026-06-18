# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_a3d.h

## Purpose
Defines the Aureal A3D register map, array sizes, ALSA control ID constants, and `a3dsrc_t` per-source state used by `au88x0_a3d.c`. It is a private driver header for the A3D block.

## Important APIs, Types, And Functions
The central type is `a3dsrc_t`, containing the parent `vortex` pointer, source/slice indices, two HRTF arrays, ITD/ILD arrays, ITD delay line, and atmospheric filter parameters. Type aliases include `a3d_Hrtf_t`, `a3d_ItdDline_t`, `a3d_atmos_t`, `a3d_LRGains_t`, `a3d_Itd_t`, and `a3d_Ild_t`. The register constants cover A and B source banks, slice VDB source/destination tables, slice control, and pointer registers. Address macros `a3d_addrA`, `a3d_addrB`, and `a3d_addrS` encode the slice/source register geometry.

## Control Flow
This header has no executable control flow. It drives all address arithmetic in the implementation: source setters combine `slice`, `source`, and a register constant to issue MMIO writes. The `CTRLID_*` constants are assigned to ALSA control `numid` fields during A3D control registration.

## State And Persistence
`a3dsrc_t` is allocated as part of the runtime `vortex_t` device structure. All fields are volatile driver state and are rebuilt on hardware init. The macro-defined register offsets describe persistent hardware address layout, not persistent data.

## Dependencies And Integration Points
The header expects kernel integer types to be available via including translation units. It is consumed by A3D implementation, core init, and any code that needs the `a3dsrc_t` shape inside `vortex_t`.

## Risks
The address macros rely on undocumented source/slice strides from reverse engineering. Comments note uncertain source sizes (`0x3A4`, `0x2C8`) and dangerous debug registers. Control IDs are not namespaced beyond this driver and are assigned directly to `id.numid`, which is unusual for ALSA controls.

## Test Signals
Build coverage should catch type and macro users. Runtime validation is indirect: A3D register writes must land in the expected source/slice, and all 16 sources should initialize without corrupting adjacent hardware blocks.
