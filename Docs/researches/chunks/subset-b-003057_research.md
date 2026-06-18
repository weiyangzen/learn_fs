# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 128881-131412

## Scope

This chunk is part of AMDGPU's generated NBIO 6.1 shift/mask register header. It contains C preprocessor constants only: no executable code, no structs, no functions, and no local storage. The covered range starts at the tail of the `DWC_E12MP_PHY_X4_NS_X4_3_RAWCMNX_DIG_MEM_CMN5` table, continues through the `CMN6` common-memory table and lane-x PHY control/status definitions for the `X4_3` PHY namespace, then switches to `KPFIFO3`, `KPNP_SNPS3`, and the first per-VF NBIF windows for `BIF_BX_DEV0_EPF0_VF0` through the beginning of `VF4_BIF_TRANS_PENDING`.

The chunk has 2,018 `#define` rows: 1,009 `__SHIFT` definitions and 1,009 `_MASK` definitions. That balance hides two chunk-boundary artifacts: line 128881 is the `DATA_MASK` for `DWC_E12MP_PHY_X4_NS_X4_3_RAWCMNX_DIG_MEM_CMN5_B7_R28`, whose shift is in the previous chunk, and line 131412 begins `BIF_BX_DEV0_EPF0_VF4_BIF_TRANS_PENDING` with a shift whose remaining fields and masks are in the next chunk.

## Purpose

The header describes hardware bit positions for NBIO 6.1 registers used by AMDGPU's PCIe/NBIO, virtualization, and power-management paths. This chunk specifically maps:

- Synopsys/DWC E12MP x4 PCIe PHY common and lane-x fields for common memory rows, common reset, PLL bandwidth/spread-spectrum overrides, PCS/PMA handshakes, RX/TX lane state, calibration, adaptation, IRQ, and controller timing.
- LCU `KPFIFO3` transmit FIFO fields used to describe FIFO hardware versioning, lane link IDs, FIFO depth/read-pointer offsets, bypass/init/standalone modes, debug bits, and PHY soft reset.
- LCU `KPNP_SNPS3` fields used for PHY versioning, lane identity, lane TX/RX request and acknowledge handshakes, PMA controls, lane/PHY soft resets, and reset-register behavior on DXIO PHY reset.
- NBIF virtual-function register windows for VF0 through VF4, including indirect MMIO index/data registers, bus-master/atomic error status, doorbell self-ring GPA aperture setup, HDP coherency flush registers, GPU HDP flush request/done bits, transaction-pending status, mailbox message buffers/control/interrupts, and VM/HV mailbox bits.

The constants let callers compose register writes and decode register reads without hard-coding numeric bit fields. The state itself lives in hardware; this file supplies metadata for the compiler and driver helpers.

## Important APIs, Types, and Macros

There are no functions, types, or runtime APIs in this range. The API surface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` is the field's least-significant bit.
- `<REGISTER>__<FIELD>_MASK` is the field mask in its encoded position.

Important macro families in this chunk:

- `DWC_E12MP_PHY_X4_NS_X4_3_RAWCMNX_DIG_MEM_CMN5_B7_R28` through `CMN5_B7_R31` and `RAWCMNX_DIG_MEM_CMN6_B0_R0` through `CMN6_B6_R31`: common-memory rows. Complete rows expose `DATA` at shift `0x0` with mask `0xFFFFL`.
- `DWC_E12MP_PHY_X4_NS_X4_3_RAWCMNX_DIG_CMN_CTL`: common PHY functional reset via `PHY_FUNC_RST`.
- `RAWCMNX_DIG_MPLLA_*` and `RAWCMNX_DIG_MPLLB_*`: PLL A/B bandwidth override, spread-spectrum range, fractional-N control, SSC clock selection, SSC override enable, and SSC enable override fields.
- `RAWLANEX_DIG_PCS_XF_TX_*` and `RAWLANEX_DIG_PCS_XF_RX_*`: PCS-side TX/RX request, reset, P-state, low-power detect, width, rate, MPLL selection/enables, VCO/reference load overrides, RX adaptation request/continuous mode, equalization values, directed TX pre/main/post values, lane number, and acknowledge/status bits.
- `RAWLANEX_DIG_FSM_*`: FSM override controls, memory address monitor, status monitor, fast RX startup/adaptation/AFE/DFE/bypass/reference/IQ/VCO stages, fast TX common-mode/RX-detect stages, and common-calibration status.
- `RAWLANEX_DIG_AON_*`: always-on analog/adaptation values, including AFE IDAC offsets, DFE even/odd phase/data/bypass/error VDAC offsets, RX phase adjust, MPLL coarse tune, RTUNE values, initial power-up done, RX adaptation values for ATT/VGA/CTLE/DFE taps 1-5, adaptation done, fast flags, slicer control, lane common-calibration status, and generic `ADPT_CTL_0` through `ADPT_CTL_7` full-word fields.
- `RAWLANEX_DIG_IRQ_CTL_*`: lane IRQ request/status, clear, reset-return request, and mask fields for RX reset, request, rate, P-state, adaptation request, and adaptation-disable events.
- `RAWLANEX_DIG_PMA_XF_*`, `RAWLANEX_DIG_TX_CTL_*`, and `RAWLANEX_DIG_RX_CTL_*`: PMA handoff and override fields, lane MPLL enable/status, supervisor state, TX/RX request/reset acknowledge, RTUNE request, TX FSM timing, TX clock selection, RX FSM enable, LOS mask timing, RX data-enable override timing, and continuous OFFCAN/adaptation status.
- `KPFIFO3_PRI_TX_FIFO_*`: FIFO hardware revision/version fields and four lane-control registers with matching `LinkID`, `FIFORdPtrOffset`, `FIFODepth`, `FIFOBypass`, `FIFOInitMode`, `Standalone`, and `HwDebug0` through `HwDebug4` fields.
- `KPNP_SNPS3_KPNP_*`: version and PHY-info fields, node lane range, per-lane TX/RX request and acknowledge bits for lanes 0-3, PMA disable controls, RX VREF, TX vboost, staggering controls, PHY and lane soft resets, and reset-on-DXIO-PHY-reset control.
- `BIF_BX_DEV0_EPF0_VF{0,1,2,3,4}_*`: per-VF NBIF fields. VF0 through VF3 are complete in this chunk for the listed SYSPFVFDEC and BIFPFVFDEC1 registers. VF4 is complete through `GPU_HDP_FLUSH_DONE` and starts `BIF_TRANS_PENDING`.

The constants are consumed through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `REG_FIELD_MASK`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and ring packet helpers that poll or write MMIO registers. Companion generated headers provide register addresses and defaults.

## Control Flow

There is no C control flow in this chunk. The implied hardware/driver control flow is:

1. Driver code chooses a register address from a companion address header, often through SOC15/NBIO/NBIF helpers.
2. It uses this header's `_MASK` and `__SHIFT` constants to extract a field, prepare a shifted value, or preserve unrelated bits during read-modify-write.
3. It writes control fields such as reset, override enable, lane request, mailbox acknowledge, or HDP flush request.
4. It polls status fields such as ACK, DONE, transaction-pending, IRQ, mailbox valid/ack, or HDP flush done until the hardware reaches the expected state.

For the PHY portion, the practical flows are PCIe PHY bring-up, link training, receiver calibration/adaptation, lane power-state changes, PLL/SSC control, PMA/PCS request and reset handshakes, lane IRQ masking/clearing, and low-level diagnostics.

For `KPFIFO3` and `KPNP_SNPS3`, the flows are lane FIFO configuration, PHY/lane reset sequencing, and request/acknowledge handshakes across four lanes.

For the NBIF VF portion, the flows are SR-IOV or virtual-function MMIO access, VF doorbell aperture setup, transaction drain checks, HDP cache coherency flushes, and host/hypervisor mailbox messaging. In-tree patterns in neighboring NBIO/NBIF implementations use the HDP flush done masks to populate `amdgpu_hdp_flush_reg` tables and use mailbox valid/ack fields in MXGPU message handling.

## State and Persistence

This header owns no mutable state. It does not allocate memory, perform I/O, lock, or persist anything. The state described by these constants is hardware state:

- PHY configuration/state: common memory rows, PLL override settings, PCS/PMA override values, lane FSM state, calibration/adaptation readbacks, RTUNE values, IRQ latches and masks, and reset/clock controls.
- LCU lane/FIFO state: FIFO sizing and bypass/init settings, lane link IDs, lane TX/RX request and acknowledge state, lane/PHY reset bits, PMA disable controls, and hardware revision/version readbacks.
- VF/NBIF state: indexed MMIO access windows, bus-master and atomic error latch/clear bits, doorbell GPA aperture base/control, HDP coherency flush request and completion state, pending master/slave transactions, transmit/receive mailbox buffers, mailbox valid/ack bits, mailbox interrupt enables, and compact VM/HV mailbox message/valid/ack bits.

Retention across GPU reset, BACO, suspend/resume, PCIe hot reset, SR-IOV VF reset, or DXIO PHY reset is hardware-specific and controlled by the surrounding AMDGPU reset/resume and virtualization code. The `KPNP_SNPS3_REG_RST_CTRL__reset_regs_when_dxio_phy_rst_MASK` field explicitly indicates that some KPNP register state may be reset as part of DXIO PHY reset behavior.

## Dependencies and Integration Points

Direct dependencies are the C preprocessor and AMD's generated register naming scheme. Runtime integration depends on the files that include this generated header and the companion address/default headers:

- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c` includes this header for NBIO 6.1 register access.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c` includes it for SR-IOV/MXGPU mailbox and virtualization paths.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h` include it for power-management register definitions.
- Companion generated files such as `nbio_6_1_offset.h`, `nbio_6_1_smn.h`, and `nbio_6_1_default.h` provide addresses and reset/default values for the same register names.
- Adjacent chunks of this same header are required to make whole-register claims at the boundaries: the prior chunk owns the `CMN5_B7_R28` shift, and the next chunk completes `VF4_BIF_TRANS_PENDING` and later VF definitions.

The VF register layout mirrors NBIF/NBIO patterns found in other ASIC generations. The HDP flush masks map CP0-CP9 and SDMA0-SDMA1 engines; these bits are used by command processor and SDMA paths to request/poll HDP cache flushes. Mailbox fields match MXGPU-style transmit/receive valid and acknowledge handshakes. Doorbell GPA aperture fields integrate with queue notification and virtualization address-window setup.

## Risks

- Generated-header drift is high impact. A wrong shift or mask can silently target the wrong hardware bit and break PCIe link training, reset sequencing, mailbox handshakes, HDP flush completion, or VF doorbell routing.
- The chunk is heavily repetitive. Common-memory rows, KPFIFO lane-control rows, KPNP lane request/ack rows, and VF0-VF4 register blocks should be mechanically checked for symmetry. A suffix or mask copied from the wrong lane/VF would compile cleanly but decode the wrong register semantics.
- Boundary splits are easy to mishandle. This chunk starts with a mask-only row from `CMN5_B7_R28` and ends after only the first shift of `VF4_BIF_TRANS_PENDING`.
- Reserved fields are explicitly named in the PHY area. Driver code should avoid writing nonzero reserved bits unless the hardware sequence requires it.
- Override and reset fields are sensitive. PLL, PCS/PMA, lane request/reset, PHY reset, KPNP soft reset, and common PHY reset bits can wedge link bring-up or require a broader device reset if programmed incorrectly.
- Status and clear fields can have hardware-specific side effects. `*_IRQ_CLR`, `CLEAR_*`, mailbox ACK, transaction pending, and HDP flush request/done fields should not be treated as ordinary read/write storage without checking the ASIC programming guide.
- VF register definitions affect isolation-sensitive paths. Doorbell aperture base/size/mode and mailbox buffer/control masks must align with hardware so one VF cannot receive incorrect doorbell or mailbox routing.
- The `BIF_ATOMIC_ERR_LOG` fields pair status bits with clear bits in the high halfword. Read-modify-write helpers that preserve stale clear bits can unintentionally clear or fail to clear error latches.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus hardware smoke testing:

- Build AMDGPU with NBIO 6.1, SR-IOV/MXGPU, and Vega powerplay include paths enabled to catch missing or misspelled macros.
- Mechanically verify that all complete registers in this range have paired `__SHIFT` and `_MASK` definitions, while allowing the known first and last boundary splits.
- Compare this chunk against `nbio_6_1_offset.h`, `nbio_6_1_smn.h`, and `nbio_6_1_default.h` so every field belongs to an address/default entry with the same register name.
- Check common-memory rows for contiguous `CMN5_B7_R29` through `CMN6_B6_R31` coverage, `DATA` shift `0x0`, and mask `0xFFFFL`.
- Check lane symmetry across the `RAWLANEX` groups against the corresponding lane groups in adjacent chunks and ASIC documentation.
- Check `KPFIFO3_PRI_TX_FIFO_CONTROL_LANE_0` through `_LANE_3` for identical field positions and masks except for the lane suffix.
- Check `KPNP_SNPS3_KPNP_LANE_REQ_CONTROL`, `LANE_REQ_STATUS`, `PMA_CONTROL0`, and `LANE_SOFT_RESET` for consistent two-bit TX/RX lane patterns across lanes 0-3.
- Check `BIF_BX_DEV0_EPF0_VF0` through `VF3` block symmetry and compare VF4 after the next chunk is merged.
- Run PCIe link bring-up, speed/width reporting, ASPM/power-state transitions, GPU reset, suspend/resume, and DXIO PHY reset tests on NBIO 6.1 hardware.
- For SR-IOV, exercise VF creation/reset, VF MMIO indexing, doorbell self-ring aperture programming, mailbox transmit/receive valid/ack handshakes, and transaction drain checks.
- For HDP coherency, verify CP and SDMA flush request/done polling on rings that use CP0-CP9 and SDMA0-SDMA1 masks, watching for timeout, stale data, or reset messages in kernel logs.

## Chunk Boundary Notes

The previous chunk owns the start of `DWC_E12MP_PHY_X4_NS_X4_3_RAWCMNX_DIG_MEM_CMN5_B7_R28`; this chunk starts with that register's `DATA_MASK`, then continues with `CMN5_B7_R29` through `CMN6_B6_R31` and the rest of the PHY/KPFIFO/KPNP/VF material described above. The next chunk must complete `BIF_BX_DEV0_EPF0_VF4_BIF_TRANS_PENDING` and continue the later VF blocks before the final per-file report makes whole-file claims about the complete VF aperture set.
