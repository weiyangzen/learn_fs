# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dma_buf.h

## Purpose

`amdgpu_dma_buf.h` declares AMDGPU's PRIME/DMA-BUF public interface. It exposes export/import hooks for the DRM driver, the XGMI accessibility helper used by VM and DMA-BUF paths, and the AMDGPU-specific `dma_buf_ops` table.

## Important APIs, types, and functions

- `amdgpu_gem_prime_export(struct drm_gem_object *gobj, int flags)` exports an AMDGPU GEM object as a DMA-BUF.
- `amdgpu_gem_prime_import(struct drm_device *dev, struct dma_buf *dma_buf)` imports a DMA-BUF as a GEM object on an AMDGPU device.
- `amdgpu_dmabuf_is_xgmi_accessible(struct amdgpu_device *adev, struct amdgpu_bo *bo)` returns whether the importer can access the BO over XGMI.
- `extern const struct dma_buf_ops amdgpu_dmabuf_ops` lets other code compare or install the AMDGPU DMA-BUF operation table.

## Control flow

DRM driver setup wires the export/import declarations into PRIME hooks. VM and DMA-BUF attachment code use the XGMI helper to decide whether shared VRAM can be accessed directly or must fall back to ordinary DMA mapping/system memory paths.

## State and persistence behavior

The header owns no state. The declared functions mutate GEM/BO references, DMA-BUF attachments, reservation objects, memory placement, and VM invalidation state in their implementation.

## Dependencies and integration points

The header includes `<drm/drm_gem.h>` and relies on AMDGPU device/BO type visibility from including files. It integrates with DRM PRIME, Linux DMA-BUF, AMDGPU VM, XGMI, and TTM memory management.

## Risks and edge cases

Callers comparing `dma_buf->ops` with `amdgpu_dmabuf_ops` depend on this symbol remaining the canonical AMDGPU DMA-BUF identity. The XGMI helper must be used before assuming peer GPU VRAM is safely accessible.

## Test signals

Compile coverage across DRM driver registration, VM, and DMA-BUF code is the header-level signal. Runtime signals include successful PRIME export/import, same-device import refcount behavior, and correct XGMI vs non-XGMI mapping decisions.
