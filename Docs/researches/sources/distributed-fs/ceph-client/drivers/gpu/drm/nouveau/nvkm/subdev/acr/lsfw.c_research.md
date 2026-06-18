# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/lsfw.c

## Purpose
Loads and tracks low-secure firmware records that ACR places into WPR and later bootstraps on falcons.

## Important APIs, types, and functions
Exports `nvkm_acr_lsfw_add()`, `nvkm_acr_lsfw_del()`, `nvkm_acr_lsfw_del_all()`, `nvkm_acr_lsfw_load_sig_image_desc()`, `_v1()`, `_v2()`, `nvkm_acr_lsfw_load_bl_inst_data_sig()`, and `nvkm_acr_lsfw_load_bl_sig_net()`.

## Control flow, state, and persistence
`add()` creates or updates one LSF record per falcon id, rejecting redefinition. Loader variants fetch signature/image/descriptor blobs or assemble images from bootloader/inst/data inputs, align bootloader/app sizes, fill resident code/data offsets, and optionally capture secure-bootloader signature metadata. Records persist on `acr->lsfw` until WPR construction cleanup or error.

## Dependencies and integration points
Depends on firmware loader, nvfw LS/HSBL parsers, falcon metadata, ACR private records, and blob lifetime helpers. SEC2/NVDEC/PMU code registers firmware through these APIs.

## Risks and test signals
Alignment and descriptor interpretation feed WPR offsets directly. Signals include LS descriptor debug dumps, duplicate LSF errors, missing firmware cleanup, and WPR comparison/bootstrap success.
