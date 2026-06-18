<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/base.c

## Purpose
Implements the common GSP subdevice lifecycle, firmware-interface selection, interrupt lookup helpers, and RM state allocation.

## Important APIs, Types, And Functions
Exports `nvkm_gsp_intr_nonstall`, `nvkm_gsp_intr_stall`, `nvkm_gsp_dtor_fws`, `nvkm_gsp_load_fw`, and `nvkm_gsp_new_`. Defines subdev callbacks for oneinit/init/fini/dtor.

## Control Flow
`nvkm_gsp_new_` allocates the GSP object, constructs the subdev, loads a matching firmware interface via `nvkm_firmware_load`, stores `gsp->func`, optionally allocates `gsp->rm` with device, GPU, WPR, and API pointers, and constructs the GSP Falcon. Lifecycle callbacks delegate to selected function hooks. Interrupt helpers search `gsp->intr[]` for stall/nonstall vector data.

## State And Persistence
Persistent state includes selected function table, firmware references, RM object, interrupt table, Falcon object, and running state. Destructor releases firmware references, Falcon state, and RM memory.

## Dependencies And Integration Points
Depends on NVKM firmware loading, Falcon construction, RM interface data, and public GSP structures. Used by all generation constructors.

## Risks And Edge Cases
Required firmware load failure aborts construction. Optional hooks must be checked before use, as the base code does. RM allocations depend on the firmware interface's `rm` pointer and GPU class data.

## Test Signals
Firmware load logs, RM version log, successful Falcon constructor, lifecycle callbacks returning zero, and correct stall/nonstall interrupt lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/base.c -->
