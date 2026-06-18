# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_sh_mask.h lines 7120-9714

## Scope And Purpose

This chunk is a generated AMDGPU VCN 4.0.3 register shift/mask header segment. It has no executable C logic; it exports preprocessor constants that describe bit positions and 32-bit masks for VCN/UVD, JPEG, MMSCH, JRBC, and JMI hardware registers. Driver code combines these macros with the companion `vcn_4_0_3_offset.h` register offsets and SOC15 register access helpers to program video decode/encode, JPEG decode, power management, virtualization, RAS, ring buffer, and memory-interface state.

The range starts in the middle of the `UVD_PGFSM_STATUS` definition, then covers the full `UVD_POWER_STATUS` through `UVD_JMI4_UVD_JMI_ATOMIC_CNTL2` register mask blocks and ends at the first `UVD_JMI5_UVD_JPEG_DEC_PF_CTRL` line. In this line range there are 456 register-name groups and 2,595 source lines, most following the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit shift for a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-shifted field mask.

Because this is generated register ABI surface, the value of the file is correctness and stability rather than local algorithmic behavior.

## Register Groups

The initial UVD power and dynamic power-gating group defines status and control surfaces for VCN block power. `UVD_POWER_STATUS` exposes `UVD_POWER_STATUS`, `UVD_PG_MODE`, `UVD_CG_MODE`, `UVD_PG_EN`, RBC/software ring-buffer snoop disable bits, and `STALL_DPG_POWER_UP`. `UVD_JPEG_POWER_STATUS` mirrors the JPEG side with JPEG power status, JPEG power-gating mode, decode/encode JRBC snoop disable bits, and JPEG DPG stall. These masks are used by VCN and JPEG start/stop paths to toggle static or dynamic power gating and to poll the hardware power state.

The DPG local-memory-access and pause registers describe firmware/SRAM programming windows. `UVD_DPG_LMA_CTL`, `UVD_DPG_LMA_DATA`, `UVD_DPG_LMA_MASK`, and `UVD_DPG_LMA_CTL2` provide read/write selection, masking, auto-increment, SRAM selection, address fields, indirect access data, and 64-bit BAR write controls. `UVD_DPG_PAUSE` has JPEG and non-JPEG request/ack bits. The VCPU cache BAR/offset/VMID registers (`UVD_DPG_LMI_VCPU_CACHE_64BIT_BAR_*`, `UVD_DPG_VCPU_CACHE_OFFSET0`, `UVD_DPG_LMI_VCPU_CACHE_VMID`) describe DPG-visible firmware/cache memory placement.

The general UVD diagnostic and security group includes scratch registers `UVD_SCRATCH1` through `UVD_SCRATCH15` plus `UVD_SCRATCH32`, `UVD_FREE_COUNTER_REG`, `UVD_FW_VERSION`, `UVD_VERSION`, `UVD_REG_FILTER_EN`, and `UVD_SECURITY_REG_VIO_REPORT`. The register-filter bits gate privileged MMSCH, video, and JPEG register access. The violation report bits distinguish host, VCPU, video, DPG, JPEG, and JDPG register violations.

Fault and error handling is represented by `UVD_PF_STATUS`, VCPU error-detection registers, and RAS registers. `UVD_PF_STATUS` has page-fault occurred and clear bits for JPEG, NJ, encoders 0-5, EJPEG, JPEG2, and atomic paths. `CC_UVD_VCPU_ERR*` captures VCPU fault-detection bounds, status, clear, detect enable, TMZ debug disable, reset-on-fault, and faulting instruction address. RAS status registers record poisoned VF/PF state for VCPU/VCODEC, MMSCH, JPEG0, and JPEG1, while `UVD_RAS_CNTL_PMI_ARB` and `VCN_RAS_CNTL_MMSCH` provide status, ack, fatal-error, PMI, rearm, and ready control bits.

Addressing, counters, clocks, and feature-discovery masks include `UVD_GFX8_ADDR_CONFIG`, `UVD_GFX10_ADDR_CONFIG`, `UVD_GPCNT2_*`, `UVD_GPCNT3_*`, `UVD_VCLK_DS_CNTL`, `UVD_DCLK_DS_CNTL`, `UVD_TSC_LOWER`, `UVD_TSC_UPPER`, and `VCN_FEATURES`. `VCN_FEATURES` advertises capabilities such as video decode/encode, MJPEG decode/encode, virtualization, H.264 legacy decode, UDEC, MJPEG2 IDCT, SCLR, VP9, AV1 decode, EFC, EFC HDR-to-SDR, dual MJPEG decode, AV1 encode, and instance ID.

The VCN/JPEG doorbell and ring-buffer group defines JPEG doorbell controls `VCN_JPEG_DB_CTRL1` through `VCN_JPEG_DB_CTRL7`, `VCN_JPEG_DB_CTRL`, `VCN_RB_DB_CTRL`, `VCN_RB1_DB_CTRL` through `VCN_RB4_DB_CTRL`, `VCN_RB_ENABLE`, `VCN_RB_WPTR_CTRL`, UVD ring read/write pointer registers, output/audio/RBC ring pointers, and ring buffer enable fields. These masks encode doorbell offsets, enable bits, read-pointer select fields, doorbell enable state, and active RB lanes.

The MMSCH block starts at address block `aid_uvd0_mmsch_dec`. It defines microcode and SRAM access registers (`MMSCH_UCODE_ADDR/DATA`, `MMSCH_SRAM_ADDR/DATA`, lock bits), VF SRAM/doorbell/context layout registers, MMSCH run/reset/interrupt/control registers, VF context and GPCOM address/size registers, host and per-mailbox request/response registers, non-cache windows, last memory access diagnostics, scratch registers, and GPU IOV scheduling registers for slots 0, 1, and 2. The field names include the generated spelling `FUNCTINO_ID` and `NEXT_FUNCTINO_ID`; consumers must use the generated names exactly.

The `aid_uvd0_slmi_adpdec` block maps MMSCH non-cache local-memory-interface windows. It supplies low/high 64-bit BAR halves for NC0 through NC7, packed 4-bit VMIDs for NC0 through NC7, MMSCH LMI control bits for coherency, VM, privilege, byte swapping, read/write mode, and read/write drop, plus LMI error/status fields for unsupported length, address alignment, write clean, error length/address bits, and read/write clean.

The JRBC address blocks `aid_uvd0_uvd_jrbc1_uvd_jrbc_dec` through `aid_uvd0_uvd_jrbc7_uvd_jrbc_dec` repeat the same command-ring surface for seven JPEG ring-buffer controllers. Each JRBC instance defines RB write/read pointers, RB control (`RB_NO_FETCH`, read-pointer write enable, pre-write timer), IB size, urgent priority, reference data, conditional-read timers, soft reset/status, status interrupt enable/ack and error bits, RB/IB buffer status, IB size update, preemption command/fence data, RB size, and a scratch register.

The JMI address blocks `aid_uvd0_uvd_jmi1_uvd_jmi_dec` through `aid_uvd0_uvd_jmi4_uvd_jmi_dec` repeat the JPEG memory-interface layout for four channels, and the chunk ends at the start of JMI5. Each JMI instance provides JPEG decode page-fault control, LMI controls for JRBC and JPEG paths, drop controls, VMID assignment for IB/RB/JPEG/atomic writes, 64-bit BAR halves for JPEG read/write, JRBC RB/IB, JRBC memory-write, and JPEG preempt fence memory, preempt VMID, byte-swap controls, atomic write controls, and atomic swap controls.

## Important APIs, Types, And Functions

This chunk exports only C macros; it does not define functions, structs, enums, typedefs, variables, or inline helpers. Its effective API is the generated macro namespace consumed by AMDGPU driver code.

The companion offset header provides `reg*` names and base indices. Runtime driver code then uses helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `SOC15_WAIT_ON_RREG`, `SOC15_REG_OFFSET`, `WREG32_SOC15_DPG_MODE`, and `WREG32_SOC15_JPEG_DPG_MODE` to read, write, poll, or DPG-stage the registers. Representative consumers in the tree include `amdgpu/vcn_v4_0_5.c` for VCN power and ring setup, `amdgpu/jpeg_v4_0_5.c` for JPEG power and JRBC setup, later VCN/JPEG generation files that share compatible field names, and MMSCH headers/code that define mailbox response semantics.

## Control Flow

There is no direct control flow in the header. The control flow is implicit in hardware bring-up and teardown paths:

1. VCN or JPEG startup clears or sets anti-hang/power-status fields, enables power-gating mode, configures DPG SRAM or firmware cache windows, and waits for `UVD_POWER_STATUS` or `UVD_JPEG_POWER_STATUS` to reach the expected state.
2. Driver initialization programs address-configuration, doorbell, ring-buffer, BAR, VMID, and byte-swap fields before enabling fetch from VCN or JRBC rings.
3. MMSCH initialization or virtualization paths configure microcode/SRAM access, VF context memory, GPCOM memory, mailboxes, non-cache windows, and GPU IOV command blocks.
4. Runtime command submission advances ring write pointers; hardware updates read pointers, status, job-done bits, buffer state, and preemption/fence state.
5. Error paths inspect page-fault, RAS, VCPU error, security-violation, MMSCH LMI, JRBC status, or JMI drop/status bits and then write corresponding clear/ack bits where the hardware defines write-to-clear behavior.

The repeated JRBC and JMI blocks are intentionally instance-specific. Code must use the register offset for the active instance together with the matching mask names, not derive one channel by applying masks from an unrelated generation.

## State And Persistence Behavior

The macros themselves hold no state. They describe persistent hardware register state in the VCN/JPEG register file. Values survive until overwritten, reset, power-gated away, or reinitialized by firmware/driver resume logic. Power-gating and DPG fields are especially stateful because the driver polls them and uses them to decide when clocks, SRAM access, firmware cache, and rings can be touched safely.

Ring pointer, doorbell, BAR, VMID, and buffer-status fields represent live command processor state. Driver-side mirrors such as ring write pointers must remain coherent with hardware read/write pointer fields. After GPU reset, suspend/resume, or VCN/JPEG power loss, these fields need normal IP block reprogramming.

Fault, RAS, security, and JRBC status bits are latched diagnostic state. Many have paired clear or ack bits, but this header only names the bits; it does not encode side-effect semantics. Callers must preserve hardware-defined write-one-to-clear or write-one-to-ack behavior and avoid read/modify/write patterns that accidentally clear unrelated latched faults.

MMSCH and GPU IOV fields carry virtualization state: active VF/PF identifiers, mailbox contents, command-control words, VM busy status, context location/size, and active-function state. In SR-IOV or multi-instance configurations, stale values can affect scheduling ownership and isolation until the MMSCH path resets or explicitly reprograms them.

## Dependencies And Integration Points

The immediate dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_3_offset.h`, which supplies the register offsets and base indices for this generation. The masks are only meaningful when paired with the VCN 4.0.3 offsets and the correct IP instance.

AMDGPU integration points include:

- VCN power management and DPG mode in `drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.c`, which uses `UVD_POWER_STATUS` masks to enable/disable power gating and poll readiness.
- JPEG power and ring setup in `drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.c`, which uses `UVD_JPEG_POWER_STATUS` masks and JRBC register programming.
- Register dumps and diagnostics through `SOC15_REG_ENTRY_STR` tables, where stable register names make MMIO state observable.
- SR-IOV/MMSCH control code and headers, where mailbox response values, VF context memory, and GPU IOV scheduling registers bridge host driver state to the multimedia scheduler.
- RAS, page-fault, and reset paths, where poisoning, fault, status, clear, and ack bits provide hardware evidence for recovery decisions.

The file is also cross-generation aligned with VCN 4.x and 5.x headers. Similar register names appear in sibling headers, but offsets, available instances, and some bit layouts can differ. This chunk should therefore be treated as VCN 4.0.3-specific hardware description, not as a generic VCN contract.

## Risks And Edge Cases

The main risk is bit-layout drift. A wrong shift or mask can set the wrong hardware field, leave a block powered off, enable the wrong ring, corrupt VMID/BAR programming, mis-handle a page fault, or acknowledge the wrong error. This is particularly risky in dense packed fields such as `UVD_PGFSM_STATUS`, `VCN_RB_ENABLE`, `VCN_RB_WPTR_CTRL`, MMSCH GPU IOV command-control words, `UVD_LMI_MMSCH_NC_VMID`, and JMI swap/VMID registers.

Generated repetition is another risk. JRBC1-7 and JMI1-4 are structurally identical but must stay instance-specific. Copying masks across instances or normalizing the generated `FUNCTINO_ID` spelling would break builds or silently target the wrong register symbols.

Power-management ordering is fragile. Code using `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, DPG LMA, clock deep-sleep, and pause request/ack fields must respect hardware sequencing; touching SRAM, BARs, or rings while the block is stalled, gated, or not yet acknowledged can produce hangs.

Fault and RAS clear bits need side-effect awareness. The header exposes `*_CLEAR`, `*_ACK`, and status masks but cannot tell whether a write clears, arms, re-arms, or merely reports state. Driver changes should be checked against hardware documentation or existing generation code before changing read/modify/write behavior.

Virtualization and security fields affect isolation. Misprogrammed MMSCH VMIDs, VF context addresses, non-cache BARs, register filters, or GPU IOV active-function fields can route memory transactions to the wrong VMID or expose privileged multimedia registers to the wrong client.

## Test Signals

Build coverage should catch missing macro names in VCN/JPEG/MMSCH users, especially when the generated names are referenced by `vcn_v4_0_5.c`, `jpeg_v4_0_5.c`, debug register tables, or generation-specific headers.

Runtime validation should focus on hardware-facing behaviors:

- VCN and JPEG start/stop in static and dynamic power-gating modes complete without `SOC15_WAIT_ON_RREG` timeouts on `UVD_POWER_STATUS` or `UVD_JPEG_POWER_STATUS`.
- Suspend/resume and GPU reset restore DPG SRAM, firmware cache, BAR, VMID, doorbell, and ring pointer state.
- Video decode/encode and JPEG decode command rings advance write/read pointers and report job completion without JRBC illegal-command, memory-timeout, or preemption-status faults.
- SR-IOV or GPU IOV workloads show expected MMSCH mailbox responses, active VF IDs, VM busy state, and context sizes without cross-VF leakage.
- Fault-injection or error-reporting tests surface expected `UVD_PF_STATUS`, VCPU error, RAS poisoned VF/PF, security-violation, and MMSCH LMI status bits and clear only the intended latched conditions.
- Register-dump comparisons against AMD-generated headers or hardware specs confirm that VCN 4.0.3 offsets are paired with VCN 4.0.3 shift/mask values rather than sibling generation values.
