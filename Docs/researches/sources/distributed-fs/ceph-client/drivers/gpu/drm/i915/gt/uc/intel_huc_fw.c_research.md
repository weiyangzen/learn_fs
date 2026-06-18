# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_fw.c

## Purpose

This file handles HuC firmware binary details that are specific to GSC-enabled images and GSCCS/PXP authentication. It parses GSC CPD headers, extracts version and DMA subimage information, sends MTL-style HECI authentication packets, and delegates DG2-style GSC load/auth to PXP.

## Important APIs, Types, And Functions

`struct mtl_huc_auth_msg_in` and `struct mtl_huc_auth_msg_out` wrap GSC MTL headers around PXP 4.3 HuC auth payloads. `intel_huc_fw_auth_via_gsccs()` maps the preallocated HECI packet object, fills a PXP `NEW_HUC_AUTH` request with HuC GGTT address and size, submits through `intel_gsc_uc_heci_cmd_submit_packet()`, handles pending replies with retries, validates reply size, and accepts success or already-loaded status.

`intel_huc_fw_get_binary_info()` validates CPD marker/version/header length, walks CPD entries, reads `"HUCP.man"` version data through `intel_uc_fw_version_from_gsc_manifest()`, and records `dma_start_offset` when `"huc_fw"` points to a CSS-valid legacy subimage. `intel_huc_fw_load_and_auth_via_gsc()` handles GSC-loaded mode through PXP and status polling. `intel_huc_fw_upload()` performs legacy DMA upload unless GSC loading is selected.

## State, Dependencies, Risks, And Test Signals

State updates are made in `huc->fw.file_selected.ver`, `huc->fw.dma_start_offset`, `huc->fw` status, and the HECI packet object map. Dependencies include GSC binary header definitions, GSC HECI submission, PXP HuC load/auth, GGTT VMA offsets, GEM object mapping, and CSS/CPD formats. Risks include malformed firmware size/offset handling, CPD entry offsets that are only checked before CSS validation, retry exhaustion on pending GSC replies, accepting `OP_NOT_PERMITTED` as already-loaded, and object mapping lifetime mistakes. Test signals include GSC-enabled HuC firmware parsing, MTL GSCCS auth, DG2 PXP load/auth, bad firmware rejection, and HuC status transitioning to running.
