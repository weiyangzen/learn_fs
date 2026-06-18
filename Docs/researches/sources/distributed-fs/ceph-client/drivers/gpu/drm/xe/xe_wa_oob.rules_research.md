# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wa_oob.rules

## Purpose

`xe_wa_oob.rules` is the source rule list for generated GT out-of-band workaround metadata. These are workarounds that are not applied through the central GT, engine, or LRC register tables, but are recorded as active bits for targeted checks elsewhere in the driver.

## Important APIs, Types, and Functions

The file is not C code. Each non-indented rule starts with a workaround id such as `1607983814`, `22014953428`, or `15015404425_disable`, followed by one or more RTP-style match expressions. Indented continuation lines add alternative match expressions for the same id. The build system generates `generated/xe_wa_oob.h` and `generated/xe_wa_oob.c` from these rules. Runtime C code queries the generated ids through `XE_GT_WA(gt, id)`.

## Control Flow and State

At build time, rules are transformed into generated RTP entries and enum/count definitions. At runtime, `xe_wa_process_gt_oob()` evaluates the generated table against each GT, stores active matches in `gt->wa_active.oob`, and marks the OOB state initialized. Later code branches on those bits, for example VM creation checks `XE_GT_WA(wa_gt, 22014953428)` to force scratch-page VMs on affected DG2 G10/G12 subplatforms.

## Dependencies and Integration Points

The rule expressions depend on RTP match vocabulary such as `GRAPHICS_VERSION_RANGE`, `MEDIA_VERSION`, `PLATFORM`, `SUBPLATFORM`, `MEDIA_STEP`, `GRAPHICS_STEP`, and helper predicates like `xe_rtp_match_not_sriov_vf` and `xe_rtp_match_psmi_enabled`. Generated outputs are included by `xe_wa.c` and other code includes the generated header for ids.

## Risks and Edge Cases

Rule formatting matters because generation relies on ids and continuation indentation. Version ranges must be reviewed whenever new IP versions are enabled; broad ranges can accidentally activate OOB behavior on unsupported hardware. Disable-suffixed rules are semantically different and need careful call-site interpretation. SR-IOV and PSMI helper predicates must match the runtime context where the OOB bit is queried.

## Test Signals

Build generation should fail on malformed rules or generated count mismatches. Runtime tests should validate representative OOB bits on DG2, PVC, Xe_LPG, Xe2, Xe3, Panther Lake, and SR-IOV VF/non-VF contexts. Call-site tests should cover behavior changes controlled by OOB ids, including scratch-page forcing and PSMI-related workarounds.
