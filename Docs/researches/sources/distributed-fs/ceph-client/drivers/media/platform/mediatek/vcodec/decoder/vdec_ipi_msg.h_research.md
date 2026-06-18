## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_ipi_msg.h

Purpose: defines the decoder AP-to-firmware and firmware-to-AP IPI message ABI. These structures are the wire format used by `vdec_vpu_if.c` to initialize, start, end, reset, core-decode, deinitialize, and query decoder firmware instances.

Important APIs/types/functions: `enum vdec_ipi_msgid` reserves AP IDs from `0xA000` and VPU ack IDs from `0xB000`. Message structs include generic command/ack formats, `vdec_ap_ipi_init`, `vdec_ap_ipi_dec_start`, `vdec_vpu_ipi_init_ack`, `vdec_ap_ipi_get_param`, and `vdec_vpu_ipi_get_param_ack`. The ABI supports both legacy `vpu_inst_addr` and ABI v2 `inst_id`.

Control flow: init sends AP init with codec type and AP instance pointer; firmware replies with status, VPU instance address, ABI version, and optional instance ID. Start messages send up to three codec-specific data words. Generic commands are used for end, reset, core, core end, and deinit. Get-param sends request data and param type; firmware returns data interpreted by the VPU interface.

State and persistence behavior: messages carry remote instance identity across calls. The init ack establishes `vpu_inst_addr`, `vdec_abi_version`, and `inst_id`, which persist in `struct vdec_vpu_inst`. Parameter acks update host-side cached sizes such as frame-buffer plane sizes.

Dependencies and integration points: included by decoder firmware interface and codec backends that rely on firmware-managed VSI memory. The layout must match firmware compiled for MediaTek VPU/SCP, including 32-bit firmware expectations and 64-bit AP pointers.

Risks: any field reorder, width change, or enum renumbering breaks firmware compatibility. ABI version handling is chip-dependent: MT8173 VPU lacks valid version fields, while SCP firmware uses them. Data arrays are small and call sites must enforce bounds. Misspelled/ambiguous comments do not affect behavior but can hide ABI assumptions.

Test signals: IPI init/start/reset/get-param smoke tests with both legacy and ABI v2 firmware; negative tests for unsupported ABI versions; build checks on 32-bit and 64-bit kernels to catch padding/layout assumptions.
