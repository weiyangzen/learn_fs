<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/base.c

## Purpose
Provides the common Firmware Security Processor subdevice wrapper used to wait for secure boot and boot authenticated GSP-FMC images.

## Important APIs, Types, And Functions
Exports `nvkm_fsp_boot_gsp_fmc`, `nvkm_fsp_verify_gsp_fmc`, and `nvkm_fsp_new_`. Defines subdev lifecycle callbacks `nvkm_fsp_preinit` and `nvkm_fsp_dtor`, plus the FSP Falcon configuration using `gp102_flcn_emem_pio`.

## Control Flow
Construction stores the generation `nvkm_fsp_func`, initializes the NVKM subdev, and constructs a Falcon at base `0x8f2000`. Preinit calls the generation `wait_secure_boot` hook. GSP-FMC boot and certificate-size verification are forwarded through `fsp->func->cot`.

## State And Persistence
Persistent state is the `struct nvkm_fsp`, its function table, subdev object, and Falcon object. Hardware state lives in the FSP Falcon and its queues.

## Dependencies And Integration Points
Used by GH100/GB100/GB202 FSP constructors and by GSP initialization code that calls `nvkm_fsp_boot_gsp_fmc`.

## Risks And Edge Cases
The base layer assumes non-null function hooks for secure-boot wait and COT boot. Size mismatches prevent booting authenticated firmware.

## Test Signals
Successful FSP preinit, successful GSP-FMC boot handoff, and no Falcon constructor or secure-boot timeout failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fsp/base.c -->
