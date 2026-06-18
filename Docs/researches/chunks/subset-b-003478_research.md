# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_sh_mask.h lines 2378-4708

## Scope And Purpose

This chunk is a generated AMDGPU VCN 5.3.0 shift/mask header segment for the UVD/VCN register block. It provides C preprocessor constants that describe bit positions and masks for clock-gating, interrupt, firmware mailbox, ring-buffer, context, decode-control, scratch, audio ring-buffer, status, and busy-state registers. The companion `vcn_5_3_0_offset.h` file supplies the register offsets, while this file supplies the field layout needed to compose and decode 32-bit register values.

The range starts in the middle of the `SMP_SUVD_CGC_GATE` mask list and ends in the middle of `UVD_ENC_PIPE_BUSY`. Those partial blocks must be reconciled with adjacent chunks when the final per-file document is assembled. Within this chunk, however, the complete register-comment blocks show the local hardware contract for VCN 5.3.0 sub-block gating and interrupt/status management.

There is no executable code here. The API surface is ABI-like hardware description: downstream AMDGPU code includes this header and uses stable symbolic macro names instead of open-coded shifts and bit masks while programming VCN/JPEG firmware bring-up, ring buffers, power management, interrupt handling, virtualization mailboxes, and diagnostics.

## Register Field Groups

The first large group covers SUVD clock-gating gate masks. `SRE_SUVD_CGC_GATE` and `UVD_SUVD_CGC_GATE` repeat the 32-bit layout used by the preceding `SMP_SUVD_CGC_GATE`: core sub-block enables for `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, codec-specific H.264/HEVC/VP9/AV1 paths, `SCLR`, `UVD_SC`, `ENT`, `IME`, `EFC`, `SAOE`, `FBC_PCLK`, `FBC_CCLK`, and `SMPA`. These are one-bit fields spanning bits 0 through 31.

The `*_SUVD_CGC_GATE2` blocks add a second-generation gate layout for `AVM`, `DBR`, `ENT`, `IME`, `SAOE`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, `SMPA`, `SMP`, `SRE`, and `UVD`. Each block exposes the same fifteen one-bit fields: `MPBE0`, `MPBE1`, `SIT_AV1`, `SDB_AV1`, `MPC1`, `SRE_AV1_ENC`, `CDEFE`, `AVM_0`, `AVM_1`, `SIT_NXT_CMN`, `SIT_NXT_DEC`, `SIT_NXT_ENC`, `SMPN_ENC`, `SMPN_DEC`, and `MPCMIF`. These fields describe newer AV1 and next-pipeline clock domains shared across many VCN sub-units.

The `*_SUVD_CGC_CTRL` blocks provide mode/control masks for individual sub-block clock-gating behavior. Blocks for `AVM`, `DBR`, `EFC`, `ENT`, `IME`, `PPU`, `SAOE`, `SCM`, `SDB`, `SIT0_NXT`, `SIT1_NXT`, `SIT2_NXT`, `SIT`, `SMPA`, `SMP`, `SRE`, and `UVD` share a layout with codec and pipeline mode bits such as `SRE_MODE`, `SIT_MODE`, `SMP_MODE`, `SCM_MODE`, `SDB_MODE`, H.264/HEVC/VP9/AV1 mode bits, `SCLR_MODE`, `UVD_SC_MODE`, `ENT_MODE`, `IME_MODE`, `SITE_MODE`, `EFC_MODE`, `SAOE_MODE`, `FBC_PCLK`, `FBC_CCLK`, and `CDEFE_MODE`. This mirrors the gate blocks but controls clock-gating policy rather than only gate selection/status.

`UVD_CGC_CTRL3` extends clock-gating control with a packed `CGC_CLK_OFF_DELAY` field at bits 0-7 and single-bit mode fields for `LCM0`, `LCM1`, `MIF`, `VREG`, `PE`, `PPU`, `SMPATN`, `DRM`, and `VIDEO_ATOMIC`. These fields are likely programmed during block initialization and power-management transitions.

The GPCOM registers are firmware/system command mailbox fields. `UVD_GPCOM_VCPU_DATA0` and `UVD_GPCOM_VCPU_DATA1` expose full 32-bit VCPU data payloads. `UVD_GPCOM_SYS_CMD` contains `CMD_SEND` at bit 0, a 30-bit `CMD` payload at bits 1-30, and `CMD_SOURCE` at bit 31. `UVD_GPCOM_SYS_DATA0` and `UVD_GPCOM_SYS_DATA1` mirror the full-width system data payload registers.

The VCPU interrupt group includes `UVD_VCPU_INT_EN`, `UVD_VCPU_INT_STATUS`, `UVD_VCPU_INT_ACK`, and `UVD_VCPU_INT_ROUTE`. The enable/status/ack registers cover address faults, semaphore timeouts, software ring interrupts `SW_RB1` through `SW_RB5`, ring-buffer/controller faults, `LBSI`, `UDEC`, LMI AXI errors, `SUVD`, read-pointer writes, job starts, page faults, `IDCT`, `MPRD`, `AVM`, clock-switch, MIF hardware interrupt, firmware driver request, and firmware driver ack events. `UVD_VCPU_INT_STATUS` additionally has `GPCOM_INT` at bit 20. `UVD_VCPU_INT_ROUTE` routes MIF hardware interrupt, driver-to-firmware request, and driver-to-firmware ack events.

The SUVD interrupt group exposes `UVD_SUVD_INT_EN`, `UVD_SUVD_INT_STATUS`, and `UVD_SUVD_INT_ACK` with packed function-interrupt ranges and error bits for `SRE`, `SIT`, `SMP`, `SCM`, `SDB`, and `SMPA`. The later `UVD_SUVD_INT_STATUS2`, `UVD_SUVD_INT_EN2`, and `UVD_SUVD_INT_ACK2` provide a smaller second bank for `SMPA` and `SDB_AV1` function/error interrupts.

The encoder VCPU interrupt group defines `UVD_ENC_VCPU_INT_EN`, `UVD_ENC_VCPU_INT_STATUS`, and `UVD_ENC_VCPU_INT_ACK` for encoder `VR` and `LP` interrupts. `UVD_MASTINT_EN` gates top-level VCPU, system, encoder, and decoder interrupt paths. `UVD_SYS_INT_EN`, `UVD_SYS_INT_STATUS`, and `UVD_SYS_INT_ACK` provide system-visible interrupt masks/status/acknowledge bits for software rings, trap/status routing, semaphore faults, context writes, and writeback paths.

The control and identity registers include `UVD_DRV_FW_MSG`, `UVD_FW_DRV_MSG_ACK`, `UVD_JOB_DONE`, `UVD_CBUF_ID`, `UVD_CONTEXT_ID`, `UVD_CONTEXT_ID2`, `UVD_NO_OP`, `UVD_IOV_ACTIVE_FCN_ID`, `UVD_IOV_MAILBOX`, `UVD_IOV_MAILBOX_RESP`, `UVD_RB_ARB_CTRL`, `UVD_CTX_INDEX`, `UVD_CTX_DATA`, `UVD_CXW_WR`, `UVD_CXW_WR_INT_ID`, `UVD_CXW_WR_INT_CTX_ID`, and `UVD_CXW_INT_ID`. These fields support firmware-driver messages, job completion tracking, SR-IOV active function/mailbox communication, ring-buffer arbitration, indirect context register access, and context writeback interrupt metadata.

The ring-buffer fields define four input ring buffers and one output ring buffer. `UVD_RB_BASE_LO`, `UVD_RB_BASE_LO2`, `UVD_RB_BASE_LO3`, `UVD_RB_BASE_LO4`, and `UVD_OUT_RB_BASE_LO` use base-low fields starting at bit 6, enforcing 64-byte alignment. The corresponding high-address registers expose full 32-bit high halves, and the `UVD_RB_SIZE*` and `UVD_OUT_RB_SIZE` fields start at bit 4, indicating size granularity aligned to 16 bytes. `UVD_AUDIO_RB_BASE_LO`, `UVD_AUDIO_RB_BASE_HI`, and `UVD_AUDIO_RB_SIZE` apply the same alignment model for the audio ring buffer.

The decode-control group includes MPEG2 error/control fields, frame address and geometry registers, and picture/buffer controls: `UVD_MPEG2_ERROR`, `UVD_YBASE`, `UVD_UVBASE`, `UVD_PITCH`, `UVD_WIDTH`, `UVD_HEIGHT`, `UVD_PICCOUNT`, `UVD_MPRD_INITIAL_XY`, `UVD_MPEG2_CTRL`, `UVD_MB_CTL_BUF_BASE`, `UVD_PIC_CTL_BUF_BASE`, `UVD_DXVA_BUF_SIZE`, `UVD_SCRATCH_NP`, and `UVD_CLK_SWT_HANDSHAKE`. Most are full-width data fields; notable packed fields include `UVD_MPRD_INITIAL_XY` with 16-bit initial X/Y coordinates, MPEG2 control sub-fields for the picture structure and decode mode, DXVA row/number size fields, and clock-switch handshake bits for send/receive.

`UVD_GP_SCRATCH0` through `UVD_GP_SCRATCH23` are full-width scratch registers. They provide 24 generic 32-bit data fields for firmware-driver communication, temporary state, or diagnostics, depending on the firmware protocol active for this IP generation.

The final status group in this chunk includes `UVD_VCPU_INT_STATUS2`, `UVD_VCPU_INT_ACK2`, and `UVD_VCPU_INT_EN2` for `SW_RB6`, `UVD_SUVD_CGC_STATUS2` for second-bank clock-gating status on `SMPA`, `MPBE1`, AV1/next-pipeline, `CDEFE`, `SIT0/1/2`, and FBC clocks, `UVD_STATUS` for RBC/VCPU/GPCOM/DRM busy and request state, and the beginning of `UVD_ENC_PIPE_BUSY`, which marks encoder pipe busy bits for IME, SMP, SIT, SDB, ENT, LCM, MDM, MIF, CDEFE, BSP/BSD, and SAOE paths.

## Important APIs, Types, And Functions

This chunk exports only preprocessor macros. There are no functions, structs, enums, typedefs, global variables, or inline helpers. The generated naming convention is:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's right-shift amount.
- `<REGISTER>__<FIELD>_MASK` gives the field's already-shifted 32-bit mask.

Driver code combines these macros with register-offset symbols such as `regSRE_SUVD_CGC_GATE`, `regUVD_CGC_CTRL3`, `regUVD_GPCOM_SYS_CMD`, `regUVD_RB_BASE_LO`, `regUVD_SUVD_INT_EN2`, and `regUVD_ENC_PIPE_BUSY` from `vcn_5_3_0_offset.h`. Consumers typically use AMDGPU register helpers to read a register, mask/shift a field, then write the updated value back, or to test status/ack bits after interrupt handling.

## Control Flow

The header itself has no runtime control flow. The implied control flow appears in consumers:

1. VCN/JPEG initialization programs clock-gating gate and control registers using the `*_SUVD_CGC_GATE*`, `*_SUVD_CGC_CTRL`, and `UVD_CGC_CTRL3` fields.
2. Ring-buffer setup writes aligned base-low, base-high, and size fields for input, output, and audio ring buffers.
3. Firmware mailbox paths write `UVD_GPCOM_SYS_DATA*`, set `UVD_GPCOM_SYS_CMD__CMD` and `CMD_SEND`, then poll or handle status/ack interrupts.
4. Interrupt setup enables selected bits in `UVD_VCPU_INT_EN`, `UVD_SYS_INT_EN`, `UVD_SUVD_INT_EN`, `UVD_ENC_VCPU_INT_EN`, and the second-bank enable registers.
5. Interrupt handlers read the corresponding status registers, branch based on set masks, write matching ack bits, and may inspect `UVD_STATUS`, `UVD_SUVD_CGC_STATUS2`, or `UVD_ENC_PIPE_BUSY` to determine whether hardware is idle or stuck.
6. Context and virtualization paths use `UVD_CTX_INDEX`/`UVD_CTX_DATA`, CXW fields, and IOV mailbox fields to exchange state with firmware or virtual functions.

Because enable, status, and ack registers often have similar but not identical layouts, handlers should use the macros for the specific register being accessed rather than reusing fields from a neighboring register by name.

## State And Persistence Behavior

The macros are compile-time constants and hold no state. They describe persistent hardware register state inside the VCN block. Clock-gating modes, interrupt enables, ring-buffer base/size programming, mailbox data, scratch contents, and arbitration settings persist until the block is reset, power-gated, firmware-reinitialized, or explicitly rewritten by the driver.

Interrupt status bits represent latched hardware events until acknowledged through the corresponding `*_ACK` register. Busy/status registers such as `UVD_STATUS`, `UVD_SUVD_CGC_STATUS2`, and `UVD_ENC_PIPE_BUSY` reflect live hardware state and can change asynchronously with firmware execution, DMA/ring activity, and clock/power transitions. Scratch and mailbox registers are shared firmware-driver state, so their contents are protocol-dependent and may be meaningful across short command sequences but not across reset or firmware reload.

Ring-buffer base and size fields are especially stateful: an incorrect write can redirect firmware DMA to the wrong memory or make the firmware consume a malformed queue until the ring is reprogrammed. The low-base fields' bit-6 alignment and size fields' bit-4 alignment are part of that persistence contract.

## Dependencies And Integration Points

The immediate dependency is `drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_5_3_0_offset.h`, which defines the register addresses and base indices for the names whose field layouts appear here. This shift/mask header must be used with the matching VCN 5.3.0 offset header; mixing it with another VCN generation would silently produce wrong register programming.

AMDGPU integration points include `drivers/gpu/drm/amd/amdgpu/jpeg_v5_3_0.c`, which includes both `vcn_5_3_0_offset.h` and `vcn_5_3_0_sh_mask.h`, and broader VCN firmware support such as `amdgpu_vcn.c`, which names the `amdgpu/vcn_5_3_0.bin` firmware. SOC integration in `soc21.c` advertises the VCN 5.3.0 encode/decode codec capabilities. These files rely on the generated register layer for hardware bring-up, firmware command exchange, interrupt routing, and power-management behavior.

The field names also align with common AMDGPU helper idioms: register offsets identify what to access, masks select fields, and shifts pack or unpack values. Hardware specifications and generated register databases are the authority for these constants; the header is not self-validating.

## Risks And Edge Cases

The highest risk is a wrong bit position or mask in a generated definition. A single-bit error in clock-gating fields can leave a VCN sub-block ungated, gated while in use, or falsely reported as idle. A wrong interrupt enable/status/ack mask can cause missed events, interrupt storms, or acknowledgements of the wrong source.

The repeated `*_SUVD_CGC_GATE2` and `*_SUVD_CGC_CTRL` blocks are intentionally similar, which makes copy/paste or generation drift hard to spot in review. They should be compared against the authoritative VCN 5.3.0 register source rather than inferred from neighboring blocks.

Partial chunk boundaries are important. This range omits the beginning of `SMP_SUVD_CGC_GATE` and the tail of `UVD_ENC_PIPE_BUSY`; final research must merge this with adjacent chunks before treating either register as fully documented.

Ring-buffer address fields are alignment-sensitive. Low base fields mask off the low six bits, and size fields mask off the low four bits; callers must not pass arbitrary byte addresses or sizes without applying the hardware-required alignment. Similar full-width data fields are easy to misuse because the mask does not encode semantic constraints such as address space, firmware ownership, or write ordering.

Firmware mailbox and scratch registers are protocol-sensitive. The macros identify fields but do not specify when firmware owns a register, which writes are doorbells, or what ordering/barrier rules are required around `CMD_SEND`, interrupt ack, and scratch updates.

Ack registers may have write-one-to-clear or write-one-to-ack semantics. The header does not encode those side effects, so read/modify/write patterns must follow the hardware programming guide and existing driver conventions.

## Test Signals

There are no direct unit tests for this generated header. Useful validation signals are build and hardware integration tests:

- A kernel build covering `jpeg_v5_3_0.c` and any VCN 5.3.0 consumers catches missing or renamed macros.
- VCN/JPEG firmware load, ring initialization, encode/decode submission, and teardown should complete without firmware mailbox timeouts or invalid ring-buffer behavior.
- Interrupt tests should verify that VCPU, system, SUVD, encoder, and second-bank interrupt status bits are enabled and acknowledged through the matching register masks.
- Suspend/resume, runtime power management, and GPU reset tests should confirm clock-gating control/status fields are restored and do not leave VCN busy or inaccessible.
- Virtualization/SR-IOV tests should exercise `UVD_IOV_ACTIVE_FCN_ID`, `UVD_IOV_MAILBOX`, and `UVD_IOV_MAILBOX_RESP` paths without cross-function mailbox confusion.
- Diagnostic polling of `UVD_STATUS`, `UVD_SUVD_CGC_STATUS2`, and `UVD_ENC_PIPE_BUSY` should match expected idle/busy transitions during decode, encode, and clock-switch activity.
