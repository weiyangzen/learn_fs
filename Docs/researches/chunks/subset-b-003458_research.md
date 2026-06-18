# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/vcn/vcn_4_0_0_sh_mask.h lines 4741-7291

## Scope

This chunk covers 2,551 lines of the generated AMD VCN 4.0.0 shift/mask header. It begins inside the `uvd0_uvddec` local-memory-interface area at the tail of `UVD_LMI_SPH`, then defines the VCN/JPEG register field layouts through the start of `uvd0_slmi_adpdec`. The chunk contains 2,138 `#define` entries and is declarative hardware ABI data only: it has no C functions, structs, variables, branches, loops, allocations, locking, or direct MMIO reads/writes.

The covered register groups are:

- LMI and VCN RAS tail registers: `UVD_LMI_VCPU_CACHE_VMID`, `UVD_LMI_CTRL2`, `UVD_LMI_URGENT_CTRL`, `UVD_LMI_CTRL`, `UVD_LMI_STATUS`, LMI perf counters, ADP swap/indirect/prefetch controls, MIF reference BARs, and `VCN_RAS_CNTL`.
- `uvd0_jpegnpdec`: JPEG decode control, ring base/read/write/size registers, decode counters, SPS/output/tier configuration, JPEG interrupt enable/status bits, tiling/address-mode fields, command/data indirect registers, scratch, and decoder soft reset.
- `uvd0_uvd_jrbc_dec`: JPEG ring-buffer controller write/read pointers, ring/IB control and sizes, urgent control, conditional-read timers, status/error/trap/preempt bits, preempt fence data, and scratch.
- `uvd0_uvd_jmi_dec`: JPEG memory-interface urgent/QoS controls, page-fault handling, LMI/JMI control, decode/encode drop and clamping registers, VMID fields, many 64-bit BAR low/high pairs for JPEG/JRBC/EJRBC/encoder paths, latency/perf counters, clean status, swap controls, atomic controls, RAS controls, and JPEG2 page-fault control.
- `uvd0_uvd_jpeg_common_dec`: JPEG common reset, system interrupt enable/status/ack, memcheck interrupt enable/status/ack, master interrupt, interrupt-handler metadata, and JRBBM arbitration.
- `uvd0_uvd_jpeg_common_sclk_dec`: JPEG clock gating, dynamic clock control/status, memory low-power controls, soft reset, and four perf-bank counters.
- `uvd0_uvd_pg_dec`: VCN power-gating FSM configuration/status, power status, DPG local-memory access registers, scratch registers, firmware/version/feature/RAS status, doorbell controls, ring enable/write-pointer controls, ring pointer mirrors, and DPG LMA control.
- `uvd0_mmsch_dec`: multimedia scheduler ucode/SRAM access, VF context/GPCOM/mailbox registers, scheduler control/status, non-cache windows, last memory-access debug registers, scratch registers, GPU IOV scheduling blocks 0-2, VFID FIFOs, NACK status, and busy status.
- The first few `uvd0_slmi_adpdec` MMSCH non-cache BAR definitions for `NC0` and `NC1`.

Every field is represented by the generated pair `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. The matching `vcn_4_0_0_offset.h` file supplies the register addresses; this chunk supplies the bit layouts for composing and decoding register values.

## Purpose

The purpose of this header section is to give AMDGPU compile-time names for VCN 4.0.0 JPEG, memory-interface, power-management, interrupt, RAS, doorbell, and MMSCH register fields. Consumers use these constants through register helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `SOC15_WAIT_ON_RREG`, and DPG-mode helpers.

For example, VCN/JPEG driver code uses these definitions to:

- Stall or unstall LMI/UMC arbitration with `UVD_LMI_CTRL2__STALL_ARB_UMC_MASK`, then poll `UVD_LMI_STATUS` clean bits before reset or power transitions.
- Enable JPEG ring interrupts with `JPEG_SYS_INT_EN__DJRBC_MASK` or per-pipe variants in newer generations.
- Program JPEG clock gating with `JPEG_CGC_GATE__JPEG_DEC_MASK`, `JPEG_CGC_GATE__JPEG2_DEC_MASK`, `JPEG_CGC_GATE__JMCIF_MASK`, and `JPEG_CGC_GATE__JRBBM_MASK`.
- Poll and update VCN power state with `UVD_POWER_STATUS__UVD_POWER_STATUS_MASK`, `UVD_POWER_STATUS__UVD_PG_MODE_MASK`, and `UVD_POWER_STATUS__UVD_PG_EN_MASK`.
- Initialize or inspect MMSCH virtual-function context/GPCOM addresses, mailbox registers, GPU IOV command controls, VM busy status, and active function masks.

The header itself is not policy. It is the hardware ABI vocabulary that lets runtime code perform precise bitfield operations without open-coded constants.

## Important Macro Families

### LMI Control, Status, and Performance

`UVD_LMI_CTRL2` defines secondary LMI control bits for SPH disable, MC/UMC urgent handling, CRC reset/select, MC read/write ID selection, VCPU non-cache extension enables, SPU extra client ID, ring-engine offload, non-JPEG MIF gating, and the important `STALL_ARB_UMC` bit used by reset/power paths to stop UMC arbitration.

`UVD_LMI_CTRL` controls write-clean timer behavior, request mode, MC urgent masking/assertion, data-coherency enables for VCPU/CM/DB/IT/MIF paths, CRC controls, firmware-failure disable behavior, and MC/UMC block resets. `UVD_LMI_STATUS` exposes clean/idle/pending state, including read/write clean, raw clean, VCPU write clean, UMC read/write clean, pending MC writes, UMC UVD/AVP idle, ADP clean state, BSP write-clean bits, and CENC read clean. Runtime reset paths in VCN generations poll these clean bits before asserting resets or changing arbitration.

`UVD_LMI_URGENT_CTRL` is split into MC read, MC write, UMC read, and UMC write urgent-stall groups. Each group has enable/stall/assert fields. `UVD_LMI_PERFMON_CTRL`, `UVD_LMI_PERFMON_COUNT_LO`, and `UVD_LMI_PERFMON_COUNT_HI` provide a small LMI performance counter. `UVD_LMI_ADP_SWAP_CNTL`, `UVD_LMI_RBC_RB_VMID`, `UVD_LMI_RBC_IB_VMID`, `UVD_LMI_MC_CREDITS`, `UVD_LMI_ADP_IND_INDEX/DATA`, `UVD_LMI_PREF_CTRL`, and MIF reference BARs cover byte swapping, VMIDs, outstanding credits, indirect ADP register access, prefetch behavior, and 64-bit luma reference addressing.

### JPEG Decode and Ring Programming

The `uvd0_jpegnpdec` block starts with `UVD_JPEG_CNTL` request/error-reset bits and ring-buffer fields: `UVD_JPEG_RB_BASE`, `UVD_JPEG_RB_WPTR`, `UVD_JPEG_RB_RPTR`, and `UVD_JPEG_RB_SIZE`. The ring pointer and size fields are shifted by four bits and masked to aligned byte ranges.

Decode status/configuration includes `UVD_JPEG_DEC_CNT`, SPS width/height and chroma/subformat fields, `UVD_JPEG_RE_TIMER`, scratch, output-buffer control/read/write pointers, pitch/UV pitch, GFX8/GFX10 tiling surface fields, address-config and address-mode registers, output XY fields, GPCOM command/data registers, indirect index/data, and decoder soft reset/status.

`UVD_JPEG_INT_EN` and `UVD_JPEG_INT_STAT` have parallel layouts for normal and error events: output-buffer write-pointer increment, job available, fence value, FIFO overflow, block-count out-of-sync, EOI, HFM, reset, ECS marker, timeout, marker, format, and profile errors. These bits feed JPEG interrupt handling and are strong test signals for command submission, job completion, and malformed-stream handling.

Tier controls (`UVD_JPEG_TIER_CNTL0/1/2` and `UVD_JPEG_TIER_STATUS`) describe component IDs, sampling factors, quantization table IDs, coefficient counts, tier index/counter state, and block accounting. They are part of the JPEG parser/decoder hardware programming model rather than general driver-owned state.

### JRBC Command Processor and Preemption

`uvd0_uvd_jrbc_dec` describes the JPEG ring-buffer controller. `UVD_JRBC_RB_WPTR`, `UVD_JRBC_RB_RPTR`, and `UVD_JRBC_RB_SIZE` are the hardware-visible command ring pointers/size. `UVD_JRBC_RB_CNTL` controls fetch and read-pointer write enable. `UVD_JRBC_IB_SIZE` and `UVD_JRBC_IB_SIZE_UPDATE` describe indirect-buffer sizing, while `UVD_JRBC_RB_BUF_STATUS` and `UVD_JRBC_IB_BUF_STATUS` expose buffer valid/read/write positions.

`UVD_JRBC_RB_COND_RD_TIMER` and `UVD_JRBC_IB_COND_RD_TIMER` contain retry timer, retry interval, continuous polling, and memory-timeout enable fields. `UVD_JRBC_STATUS` is the main completion/error register with job done bits, illegal-command bits, conditional-register-read timeout, memory read/write timeout, trap status, preempt status, interrupt enable, and interrupt ack. `UVD_JPEG_PREEMPT_CMD` controls preemption enable, wait-for-job-done, and fence command behavior, with two 32-bit preempt fence data words.

These masks are used around ring startup, command submission, interrupt handling, and GPU reset diagnosis. A wrong pointer mask or status bit definition can turn a live ring into a stuck-ring or false-timeout condition.

### JMI, VMID, BAR, Swap, and Memcheck Controls

The `uvd0_uvd_jmi_dec` block covers the memory-facing path for JPEG decode/encode and JRBC/EJRBC. `UVD_JADP_MCIF_URGENT_CTRL` and `UVD_JMI_URGENT_CTRL` define watermarks, urgent timers, urgent step sizes, QoS enables, and MC read/write urgent assertion. `UVD_JMI_CTRL`, `UVD_LMI_JRBC_CTRL`, `UVD_LMI_JPEG_CTRL`, `UVD_JMI_EJRBC_CTRL`, `UVD_LMI_EJPEG_CTRL`, and `UVD_JMI_SCALER_CTRL` provide arbitration wait enables, max burst fields, read/write swap fields, MC urgent controls, CRC control, and scaler/JPEG memory behavior.

Drop and clamping registers (`JPEG_LMI_DROP`, `UVD_JMI_EJPEG_DROP`, `JPEG_MEMCHECK_CLAMPING`, `UVD_JMI_EJPEG_MEMCHECK_CLAMPING`) let hardware drop or clamp selected read/write paths to safe addresses. `JPEG_MEMCHECK_SAFE_ADDR` and `JPEG_MEMCHECK_SAFE_ADDR_64BIT` provide safe address fields. These are security and robustness sensitive because they affect behavior after memory-check or page-fault conditions.

VMID registers define which GPU VMIDs are used by JPEG/JRBC read/write/fence/atomic paths: `UVD_LMI_JRBC_IB_VMID`, `UVD_LMI_JRBC_RB_VMID`, `UVD_LMI_JPEG_VMID`, `UVD_JMI_ENC_JRBC_IB_VMID`, `UVD_JMI_ENC_JRBC_RB_VMID`, `UVD_JMI_ENC_JPEG_VMID`, `UVD_LMI_JPEG_PREEMPT_VMID`, `UVD_LMI_ENC_JPEG_PREEMPT_VMID`, and `UVD_LMI_JPEG2_VMID`. These fields are integration points with AMDGPU VM and SR-IOV isolation; an incorrect VMID mask can make hardware access the wrong address space.

The many `*_64BIT_BAR_LOW/HIGH` registers define low/high 32-bit halves for JPEG read/write, preempt fence, JRBC/EJRBC ring and IB, ring/IB memory read/write, encoder PEL read, bitstream write, scaler read/write, JPEG2 read/write, atomic user writes, and HUFF fence paths. Each low/high half exposes the full 32-bit field. Correct low-before-high or high-before-low ordering is a caller responsibility; the header only gives masks.

`UVD_JMI_DEC_SWAP_CNTL`, `UVD_JMI_ENC_SWAP_CNTL`, and `UVD_JMI_DEC_SWAP_CNTL2` define two-bit byte-swap fields per data path. `UVD_JMI_ATOMIC_CNTL` and `UVD_JMI_ATOMIC_CNTL2` control atomic arbitration, burst, drop/clamping, urgent, software gate, atomic mode, endianness, address alignment, and memory-address-type behavior.

`UVD_JMI_CLEAN_STATUS` is the JPEG memory-interface equivalent of LMI clean state. It exposes clean/raw/pending bits for LMI, DJRBC, EJRBC, JPEG, PEL, scaler, bitstream, JPEG2, and MC write pending paths. It is relevant to reset and power-down sequencing.

### JPEG Common Interrupt, Clock, and Perf Blocks

`JPEG_SOFT_RESET_STATUS`, `JPEG_SYS_INT_EN`, `JPEG_SYS_INT_STATUS`, and `JPEG_SYS_INT_ACK` define the common JPEG interrupt domain. System interrupt bits include DJRBC, EJRBC, decode/encode page-fault reports, JPEG core, JPEG2 core, and RAS control notifications. `JPEG_MEMCHECK_SYS_INT_EN/STAT/ACK` separately expose high/low read/write memory-check errors for DJRBC, EJRBC, BS fetch/write, PEL fetch, scalar read/write, output-buffer write, and JPEG2 read/write paths.

`JPEG_MASTINT_EN` controls interrupt overrun reset/status. `JPEG_IH_CTRL` describes the interrupt handler packet metadata: soft reset, stall, status clean, VMID, user data, and ring ID. `JRBBM_ARB_CTRL` provides DJRBC/EJRBC/SRBM drop controls.

The SCLK common block defines clock gating and memory low-power behavior. `JPEG_CGC_GATE` gates JPEG decode, JPEG2 decode, JPEG encode, JMCIF, and JRBBM. `JPEG_CGC_CTRL` configures dynamic clock mode, delay timers, and per-block mode bits. `JPEG_CGC_STATUS` reports VCLK/SCLK active state per block. `JPEG_COMN_CGC_MEM_CTRL`, `JPEG_DEC_CGC_MEM_CTRL`, `JPEG2_DEC_CGC_MEM_CTRL`, and `JPEG_ENC_CGC_MEM_CTRL` control light sleep, deep sleep, shutdown, and software light-sleep enables for memories. `JPEG_SOFT_RESET2` adds atomic soft reset. `JPEG_PERF_BANK_CONF`, `JPEG_PERF_BANK_EVENT_SEL`, and four count registers expose a compact perf-bank interface.

### VCN Power, Feature, RAS, Doorbell, and Ring State

The `uvd0_uvd_pg_dec` block describes power gating and DPG state. `UVD_PGFSM_CONFIG` and `UVD_PGFSM_STATUS` contain two-bit power config/status fields for many sub-blocks (`UVDM`, `UVDS`, `UVDF`, `UVDTC`, `UVDB`, `UVDTA`, `UVDLM`, `UVDTD`, `UVDTE`, `UVDE`, `UVDAB`, `UVDJ`, `UVDTB`, `UVDNA`, `UVDNB`). `UVD_POWER_STATUS` and `UVD_JPEG_POWER_STATUS` expose global and JPEG power status/mode, snoop disable bits, PG enable, clock-gating mode, and DPG power-up stall. VCN runtime power code polls and updates these fields around start/stop and dynamic power-gating paths.

`UVD_PG_IND_INDEX/DATA`, `UVD_DPG_LMA_CTL/DATA/MASK`, `UVD_DPG_PAUSE`, and `UVD_DPG_LMA_CTL2` define direct power-gating/local-memory access controls and SRAM write pointers. `UVD_DPG_LMI_VCPU_CACHE_64BIT_BAR_LOW/HIGH`, `UVD_DPG_VCPU_CACHE_OFFSET0`, and `UVD_DPG_LMI_VCPU_CACHE_VMID` define DPG VCPU cache addressing.

Scratch registers `UVD_SCRATCH1` through `UVD_SCRATCH32`, `UVD_FW_VERSION`, `UVD_VERSION`, timestamp counter low/high, and general-purpose counter registers provide firmware, diagnostic, and timing state. `UVD_PF_STATUS` exposes many page-fault status bits and fields. `UVD_RAS_VCPU_VCODEC_STATUS`, `UVD_RAS_MMSCH_FATAL_ERROR`, `UVD_RAS_JPEG0_STATUS`, `UVD_RAS_JPEG1_STATUS`, and `UVD_RAS_CNTL_PMI_ARB` describe poison/fatal/RAS control state.

`VCN_FEATURES` advertises hardware capabilities: video decode/encode, MJPEG decode/encode, virtualization, H.264 legacy decode, UDEC, MJPEG2 IDCT, scaler, VP9, AV1 decode, EFC encode, HDR2SDR, dual MJPEG decode, AV1 encode, and instance ID. Code that derives feature support from this register depends on exact masks.

Doorbell and ring controls include `VCN_RB_DB_CTRL`, `VCN_JPEG_DB_CTRL`, `VCN_RB1_DB_CTRL` through `VCN_RB4_DB_CTRL`, `VCN_UMSCH_RB_DB_CTRL`, `VCN_AGDB_CTRL0` through `VCN_AGDB_CTRL5`, and `VCN_AGDB_MASK0` through `VCN_AGDB_MASK5`. They share offset, enable, and hit fields for doorbell routing. `VCN_RB_ENABLE` enables multiple video/JPEG/UMSCH/EJPEG/audio rings, and `VCN_RB_WPTR_CTRL` enables write-pointer checksum/control-store behavior for the same ring families. Ring pointer mirror registers expose video, output, audio, RBC, and numbered RB read/write pointers.

### MMSCH and GPU IOV Scheduler

The `uvd0_mmsch_dec` block defines the multimedia scheduler register interface. `MMSCH_UCODE_ADDR/DATA` and `MMSCH_SRAM_ADDR/DATA` provide ucode and SRAM access with lock bits on address registers. `MMSCH_VF_SRAM_OFFSET`, `MMSCH_DB_SRAM_OFFSET`, and `MMSCH_CTX_SRAM_OFFSET` describe SRAM partitioning for virtual functions, doorbells, and context storage.

Interrupt and VF context/GPCOM registers include `MMSCH_INTR`, `MMSCH_INTR_ACK`, `MMSCH_INTR_STATUS`, `MMSCH_VF_VMID`, `MMSCH_VF_CTX_ADDR_LO/HI`, `MMSCH_VF_CTX_SIZE`, `MMSCH_VF_GPCOM_ADDR_LO/HI`, `MMSCH_VF_GPCOM_SIZE`, host/response mailboxes, and two per-VF mailbox pairs. `MMSCH_CNTL` exposes scheduler clock enable, error-detection enable, IRQ error field, NACK and doorbell-busy interrupt enables, probe timeout, timeout disable, and idle status.

`MMSCH_NONCACHE_OFFSET0/SIZE0` and `MMSCH_NONCACHE_OFFSET1/SIZE1` describe non-cache windows. `MMSCH_PROC_STATE1`, `MMSCH_LAST_MC_ADDR`, and `MMSCH_LAST_MEM_ACCESS_HI/LO` are debug/status registers for scheduler execution and memory access. Scratch registers provide firmware-visible storage.

GPU IOV command and status blocks repeat for scheduler blocks 0, 1, and 2: `MMSCH_GPUIOV_SCH_BLOCK_*` identify block ID/version/size; `MMSCH_GPUIOV_CMD_CONTROL_*` contains command type, execute, interrupt enables, VM-busy interrupt enable, function ID, and next function ID; `MMSCH_GPUIOV_CMD_STATUS_*`, `MMSCH_GPUIOV_VM_BUSY_STATUS_*`, `MMSCH_GPUIOV_ACTIVE_FCNS_*`, and `DW6/DW7/DW8` provide command state and data. There are parallel `*_IP_*` scheduler-block and command-status registers, context-size/location fields, VFID FIFO head/tail pairs, NACK status, mailbox data, and `MMSCH_VM_BUSY_STATUS_0/1/2`.

The chunk ends after the first `uvd0_slmi_adpdec` definitions for MMSCH non-cache BAR low/high registers. The continuation of `UVD_LMI_MMSCH_NC1_64BIT_BAR_HIGH` and later NC2-NC7/VMID fields belongs to the next chunk.

## Control Flow

There is no executable control flow in this header chunk. Runtime control flow is implied by how AMDGPU callers use the macros:

1. Resolve the register address with a companion `reg*`/`mm*` offset macro from `vcn_4_0_0_offset.h` or an ASIC-specific wrapper.
2. Read the raw 32-bit register value with `RREG32_SOC15`, `RREG32_SOC15_OFFSET`, or a DPG-mode read helper.
3. Extract fields with `REG_GET_FIELD` or manual mask/shift operations, or compose updates with `REG_SET_FIELD`, `WREG32_P`, or explicit read-modify-write.
4. For state transitions, poll status masks with helpers such as `SOC15_WAIT_ON_RREG`, then write control fields in the order required by the hardware block.

Typical flow examples from nearby VCN/JPEG generations are: program clock gates before ring setup; enable JPEG system interrupts; set ring write pointers; poll LMI/JMI clean bits before reset; update `UVD_POWER_STATUS` for DPG mode; and initialize MMSCH VF context/GPCOM pointers before GPU IOV command execution.

The header does not encode sequencing, delays, clear-on-read behavior, write-one-to-clear semantics, or serialization. Those rules live in the driver code and hardware programming guide.

## State and Persistence Behavior

The macros describe hardware register state, not storage allocated by the driver:

- Ring pointers, ring sizes, IB sizes, doorbell controls, and write-pointer controls persist in VCN/JPEG registers until reset or explicit reprogramming.
- Interrupt enable/status/ack and memcheck status/ack fields represent transient hardware event state; ack registers can have side effects depending on hardware semantics.
- Power-gating, clock-gating, and memory low-power fields persist across runtime power transitions and directly affect block availability.
- VMID and BAR fields persist as hardware address-space and buffer mappings for JPEG/JRBC/EJRBC/MMSCH paths.
- Perf counters and latency counters accumulate hardware events until reset, wrap, or reconfiguration.
- RAS and page-fault status fields capture error state that may need explicit rearm, clear, or poison handling.
- MMSCH mailbox, SRAM, GPU IOV command, busy, and active-function fields represent scheduler and virtualization state shared with firmware/hardware.

Because this file only names bitfields, the persistence risk is indirect but significant: a wrong mask can make software preserve, clear, set, or poll the wrong bits in persistent hardware state.

## Dependencies and Integration Points

Direct dependencies are the C preprocessor and the matching VCN 4.0.0 offset header. Practical integration points in this tree include:

- `drivers/gpu/drm/amd/amdgpu/jpeg_v4_0_5.c`, which uses the same generated field families for JPEG clock gating, JPEG system interrupt enable, JPEG ring write-pointer reset/read/write, and DPG-mode JPEG register programming.
- `drivers/gpu/drm/amd/amdgpu/vcn_v4_0_5.c`, which uses `UVD_LMI_CTRL2`, `UVD_LMI_STATUS`, `UVD_POWER_STATUS`, `UVD_PGFSM_CONFIG`, and related masks for VCN power, reset, clock, and LMI clean sequencing.
- Newer VCN/JPEG implementations such as `vcn_v5_0_1.c`, `vcn_v5_0_2.c`, `jpeg_v5_0_2.c`, and `jpeg_v5_3_0.c`, which preserve the same programming pattern and show how these generated field names are consumed as the IP evolves.
- `drivers/gpu/drm/amd/amdgpu/mmsch_v2_0.h` and VCN virtualization paths, which define/use MMSCH register offsets corresponding to this scheduler and GPU IOV field layout.
- AMDGPU register helper infrastructure (`REG_GET_FIELD`, `REG_SET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_P`, `SOC15_WAIT_ON_RREG`, and DPG-mode helpers), which assumes every generated `_MASK` and `__SHIFT` pair matches the underlying register.
- Firmware and hardware interfaces for VCN, JPEG, MMSCH, RAS, page-fault reporting, and SR-IOV/GPU IOV scheduling.

The generated header must stay synchronized with the offset header and with ASIC-specific source files. A field layout from VCN 4.0.0 used with a VCN 4.0.5 or VCN 5.x address is only safe when the hardware field layout is intentionally unchanged.

## Risks and Edge Cases

- Large generated ABI surface: this chunk has more than two thousand macros. Mechanical generation errors can compile cleanly while corrupting runtime bitfield access.
- Partial chunk boundaries: line 4741 starts after the `UVD_LMI_SPH` comment and shift definitions, so this chunk only contains the end of that register. The end also cuts into the `uvd0_slmi_adpdec` BAR sequence after `NC1`. Merge/reconciliation should combine adjacent chunks before treating those registers as fully researched.
- Read-modify-write hazards: control registers mix enable, reset, urgent, stall, CRC, drop, clamping, and ack-like fields. Broad writes can accidentally reset blocks, acknowledge interrupts, disable clocks, drop traffic, or change QoS.
- Pointer and alignment masks: JPEG/JRBC ring pointers, BAR low fields, and MMSCH context/GPCOM low-address fields encode alignment in low bits. Using raw byte addresses without respecting shifts/masks can misprogram hardware addresses.
- VMID isolation risk: JPEG/JRBC/EJRBC/MMSCH VMID fields are security-sensitive in virtualized or multi-process GPU contexts. Wrong masks can route hardware reads/writes through the wrong VMID.
- Interrupt status/ack confusion: `JPEG_SYS_INT_STATUS`, `JPEG_SYS_INT_ACK`, `JPEG_MEMCHECK_SYS_INT_STAT`, and `JPEG_MEMCHECK_SYS_INT_ACK` have similar layouts. Accidentally using status masks as write data for the wrong ack register can lose diagnostics or leave interrupts asserted.
- Clean-status polling risk: `UVD_LMI_STATUS` and `UVD_JMI_CLEAN_STATUS` expose many similar clean/raw/pending bits. Waiting on the wrong bit can cause reset hangs or premature reset while memory traffic is still pending.
- Power and clock sequencing risk: `UVD_POWER_STATUS`, `UVD_JPEG_POWER_STATUS`, `JPEG_CGC_GATE`, and memory low-power fields require hardware-specific ordering. This header cannot prevent writes while the block is gated or powered down.
- RAS and page-fault side effects: RAS, poison, page-fault, memcheck, and clamping fields may be sticky or require rearm/ack sequences. Incorrect masks can hide hardware faults or repeatedly retrigger interrupts.
- Naming typo preservation: GPU IOV command control fields use the generated spelling `FUNCTINO_ID` rather than `FUNCTION_ID`. Consumers must use the generated name exactly unless the register generator is corrected across all dependent files.

## Test Signals

Useful validation for this chunk is mostly compile-time, static, and hardware-integration oriented:

- Build AMDGPU with VCN 4.0 support so all `UVD_*`, `JPEG_*`, `VCN_*`, and `MMSCH_*` field macros referenced by VCN/JPEG/MMSCH code resolve with the matching offset headers.
- Compare generated `vcn_4_0_0_sh_mask.h` against AMD's register database or a known-good upstream header; focus on high-risk families: ring pointers, VMIDs, BAR halves, interrupt ack/status, power status, clean status, and MMSCH GPU IOV controls.
- Boot supported VCN 4.x hardware and verify VCN/JPEG initialization: clock-gating writes, DPG-mode programming, JPEG ring write-pointer reset/readback, and interrupt enable should complete without ring timeout.
- Exercise JPEG decode submissions and confirm `UVD_JRBC_RB_WPTR/RPTR`, `UVD_JRBC_STATUS` job-done/error bits, and `JPEG_SYS_INT_STATUS/ACK` behave as expected.
- Test malformed or fault-injected JPEG paths where available: memcheck status/ack bits, page-fault report bits, clamping/drop behavior, and RAS JPEG status should produce stable diagnostics without interrupt storms.
- Run suspend/resume, runtime DPG, and GPU reset paths while JPEG/VCN rings are idle and active; failures often show up as waits on `UVD_LMI_STATUS`, `UVD_JMI_CLEAN_STATUS`, `UVD_POWER_STATUS`, or `UVD_JPEG_POWER_STATUS`.
- On SR-IOV/GPU IOV configurations, validate MMSCH VF context/GPCOM address programming, mailbox exchange, GPU IOV command status, VM busy status, active function masks, and VFID FIFO state.
- Review any future generated-header churn together with `vcn_4_0_0_offset.h` and ASIC-specific C files. Field changes in this chunk should be treated as hardware ABI changes, not formatting-only edits.
