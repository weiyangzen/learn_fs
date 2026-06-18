# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_uclo.h

## Purpose
`icp_qat_uclo.h` defines constants and parsed object layouts for QAT microcode loader objects: UOF, SUOF, MOF, CSS headers, signed image metadata, AE modes, init tables, register tables, firmware authentication descriptors, and multi-object containers.

## Important APIs, Types, And Functions
Important constants define device type masks, maximum AE/context/uimage/ustore/register counts, object IDs and versions, chunk names, signature/key lengths for CSS/DSS, dual-sign metadata sizes, and AE mode extraction macros. Major structures include `icp_qat_uclo_objhandle`, `icp_qat_uof_filehdr`, `icp_qat_uof_objhdr`, `icp_qat_uof_image`, `icp_qat_uclo_encapme`, `icp_qat_uof_code_page`, `icp_qat_uof_batch_init`, `icp_qat_suof_handle`, `icp_qat_suof_img_hdr`, `icp_qat_fw_auth_desc`, `icp_qat_auth_chunk`, `icp_qat_css_hdr`, `icp_qat_simg_ae_mode`, and MOF table/header structures.

## Control Flow
The header has no executable control flow. Firmware loader code parses file headers and chunks, builds string/object tables, maps UOF code pages and init memory/register symbols, selects SUOF signed images for AE masks, creates authentication descriptors, and loads/authenticates firmware through HAL/FCU paths.

## State And Persistence Behavior
Parsed handles persist for the firmware loading/session lifetime. They reference buffers containing firmware objects, decoded strings, uwords, image tables, init-memory lists, and per-AE page/region state. CSS/auth structures represent staged firmware authentication metadata. No disk persistence is performed by this header.

## Dependencies And Integration Points
It is included by firmware loader handle and HAL headers. It integrates firmware file formats with accelerator-engine programming, CSS authentication, and generation-specific loader behavior.

## Risks
The structures mirror binary firmware formats, so padding, field widths, and endian assumptions are critical. Many fields are raw offsets into firmware buffers; parser bounds checks outside this header must be strict. Signature/key length macros vary by CSS 2K/3K and dual-sign support, so wrong chip flags can misplace image offsets.

## Test Signals
Firmware load tests across UOF/SUOF/MOF images, signed/dual-signed images, CSS 2K/3K variants, and multiple AE masks validate this ABI. Fuzzing or malformed firmware-object tests should check parser bounds and chunk validation.
