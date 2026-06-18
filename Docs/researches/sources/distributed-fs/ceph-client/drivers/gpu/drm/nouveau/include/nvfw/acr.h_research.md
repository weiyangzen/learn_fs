
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvfw/acr.h

## Purpose
Defines firmware data structures for NVIDIA ACR/WPR and light-secure falcon boot metadata parsed by Nouveau's firmware loader.

## Important APIs, types, and functions
- WPR headers: `struct wpr_header`, `wpr_header_v1`, `wpr_generic_header`, and `wpr_header_v2` with status and identifier constants.
- Signature and LSB headers: `struct lsf_signature`, `lsf_signature_v1`, `lsb_header_tail`, `lsb_header`, `lsb_header_v1`, and the large `lsb_header_v2` with signature, encryption, manifest, and FMC fields.
- ACR descriptors: `struct flcn_acr_desc` and `flcn_acr_desc_v1` describe WPR regions, region permissions, ucode blob, and VPR/HDCP policy.
- Dump prototypes expose structured debug output for each major format.

## Control flow
This header is declarative. Parser/dump implementations use the struct definitions to interpret binary firmware blobs and WPR contents, branching on versioned headers and generic header IDs.

## State and persistence
No live driver state is stored. The structures mirror persistent firmware blob layouts and WPR metadata consumed during secure falcon bootstrap.

## Dependencies and integration points
Uses `u8/u16/u32/u64` kernel types and `struct nvkm_subdev` for dump routines. It integrates with Nouveau's `nvfw` parsing code, ACR bootstrap, PMU/SEC2 command paths, and secure firmware loading for falcons.

## Risks
Binary layout compatibility is critical; missing packing/alignment on fields with `u64 __aligned(8)` or nested signature blobs can break parsing. Versioned formats have many similar fields, increasing copy/paste and wrong-version risks. Security-sensitive fields include signatures, dependency maps, encryption IVs, WPR permissions, and HDCP/VPR policy.

## Test signals
Firmware load should parse and dump expected WPR/LSB/ACR versions on supported GPUs. Negative tests should reject invalid status, signature, size, or offset fields. Secure boot failures usually surface as ACR validation or falcon bootstrap errors.
