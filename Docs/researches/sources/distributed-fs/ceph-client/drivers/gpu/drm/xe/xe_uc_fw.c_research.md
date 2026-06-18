# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw.c

Purpose: Implements firmware selection, request, parsing, validation, copying, upload, and printing for GuC, HuC, and GSC microcontroller firmware.

Important APIs/types/functions: Public APIs are `xe_uc_fw_init`, `xe_uc_fw_copy_rsa`, `xe_uc_fw_upload`, `xe_uc_fw_check_version_requirements`, and `xe_uc_fw_print`. Key internal pieces include firmware definition macros/tables, `uc_fw_auto_select`, `uc_fw_override`, `uc_fw_vf_override`, `uc_fw_request`, CSS/GSC parsing helpers (`parse_css_header`, `parse_cpd_header`, `parse_gsc_layout`, `parse_headers`), `uc_fw_copy`, `uc_fw_xfer`, and `uc_fw_fini`.

Control flow: Firmware init starts with autoselection by platform/GT type, applies user module-parameter overrides, handles SR-IOV VF preloaded firmware, marks unsupported/disabled states, requests the blob, parses CSS or GSC headers, checks versions, copies the firmware into a managed GGTT BO, and registers cleanup that reverts status to selected. Upload asserts the firmware is not already loaded, validates loadability, DMA-transfers the CSS header plus uCode from GGTT to WOPCM, marks `TRANSFERRED`, or marks `LOAD_FAIL` on error. Printing emits path, status, wanted/found versions, and component sizes.

State and persistence behavior: Mutates `struct xe_uc_fw`: path, user override flag, wanted/found versions, version type, full-version requirement, `has_gsc_headers`, size, BO pointer, RSA/uCode/CSS offsets, private data size, build type, and firmware status. Firmware blobs are released after copying. BO lifetime is DRM-managed. VF mode marks GuC/HuC as preloaded and suppresses local paths.

Dependencies and integration points: Uses Linux firmware loader, DRM managed actions, Xe module params, platform metadata, GT/device helpers, SR-IOV VF queries, Xe BO creation, GGTT addresses, force-wake/MMIO DMA registers, GSC/HuC/GuC ABI structures, and `linux-firmware` filenames declared with `MODULE_FIRMWARE`.

Risks: Firmware filename tables must stay ordered newest-to-oldest and platform-correct. Header parsing must validate all sizes before dereferencing untrusted firmware data. Version policy differs for force-probed/full-version-required platforms, major-only supported platforms, HuC no-version filenames, and GSC compatibility versions. DMA upload requires force-wake and correct GGTT/WOPCM offsets. User overrides bypass version failure in `xe_uc_fw_check_version_requirements`, increasing diagnostic importance.

Test signals: Boot each supported platform with matching, missing, old-minor, wrong-major, malformed CSS, malformed GSC CPD/BPDT, user override, disabled uC, and SR-IOV VF configurations. Validate status transitions, logs, BO creation, RSA copy size, DMA register programming, timeout handling, and debugfs/print output.
