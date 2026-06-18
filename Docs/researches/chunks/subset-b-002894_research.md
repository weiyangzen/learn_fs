# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h lines 8701-11799

## Scope

This chunk covers a generated AMD NBIO 2.3 default-value header section. It starts at the first `cfgBIF_CFG_DEV0_EPF0_VF10_0_*_DEFAULT` macro and covers 2,754 C preprocessor constants through `mmBIF_BX_DEV0_EPF0_VF23_HDP_REG_COHERENCY_FLUSH_CNTL_DEFAULT`.

The range has two major parts:

- Lines 8701-10421 define PCI configuration-space reset/default values for SR-IOV virtual functions `VF10` through `VF30` under `nbio_nbif0_bif_cfg_dev0_epf0_vf*_bifcfgdecp`.
- Lines 10422-11799 define per-VF MMIO/RCC/BIF defaults for `VF0` through the first part of `VF23`, covering `SYSPFVFDEC`, `BIFPFVFDEC1`, and `BIFDEC2` address blocks.

The file is data-only C preprocessor material. It defines no functions, structs, variables, locks, allocations, or direct register accesses. Its public interface is the generated `<register>_DEFAULT` macro convention used with matching NBIO address and shift/mask headers.

## Purpose

`nbio_2_3_default.h` records hardware reset/default values for the NBIO 2.3 register namespace used by AMDGPU. In this chunk, the defaults describe how SR-IOV virtual functions initially expose PCIe configuration space and per-VF NBIO facilities before runtime driver, firmware, host, or guest software programs them.

The PCI config-space defaults give each covered VF a mostly disabled or zeroed function image, with a small set of nonzero capability-list and identity defaults. For `VF10` through `VF30`, each VF repeats the same 79 `cfgBIF_CFG_DEV0_EPF0_VF*_0_*_DEFAULT` entries. Nonzero values include:

- `ADAPTER_ID_DEFAULT` as `0x73101002`, carrying an AMD vendor-oriented adapter identity value in the generated config image.
- `CAP_PTR_DEFAULT` as `0x00000048`.
- PCIe capability-list and MSI capability-list links such as `PCIE_CAP_LIST_DEFAULT` `0x0000a000` and `MSI_CAP_LIST_DEFAULT` `0x0000c000`.
- `PCIE_CAP_DEFAULT` `0x00000002`, `LINK_CAP_DEFAULT` `0x00000d04`, `DEVICE_CAP2_DEFAULT` `0x00010000`, `LINK_CAP2_DEFAULT` `0x0000001e`, and `MSI_MSG_CNTL_DEFAULT` `0x00000082`.
- Enhanced capability-list pointers such as vendor-specific `0x11000000`, advanced error reporting `0x20020000`, and ATS `0x2c000000`.

The per-VF MMIO/RCC/BIF defaults then describe the reset state for host-visible or function-visible control/status areas: indirect MMIO index/data windows, RCC error/logging and doorbell aperture controls, BIF bus-master/atomic status, self-ring doorbell GPA aperture registers, HDP coherency flush registers, mailbox transfer/receive buffers, VF mailbox interrupt control, and GFX MSI-X table/PBA defaults.

## Important Macro Families

### VF PCI Configuration Defaults

`cfgBIF_CFG_DEV0_EPF0_VF10_0_*_DEFAULT` through `cfgBIF_CFG_DEV0_EPF0_VF30_0_*_DEFAULT` provide the virtual PCI function's generated defaults. Each VF includes conventional PCI header fields such as vendor ID, device ID, command, status, revision, class code, cache line, latency, header, BIST, BARs, ROM base, interrupt line/pin, min grant, and max latency.

The same block also covers PCIe capability state:

- Base PCIe capability and link/device capability/control/status defaults.
- PCIe Capability 2 link/device defaults.
- MSI and MSI-X capability defaults. MSI has a nonzero message-control default, while MSI-X capability/table/PBA defaults are zero in these config-space blocks.
- Vendor-specific, AER, ATS, and ARI enhanced capability defaults. AER status/mask/severity/header-log and TLP-prefix log values reset to zero; ARI defaults are zero; ATS has a nonzero enhanced-capability list pointer but zero capability/control defaults.

Most config fields are `0x00000000`. The repeated nonzero capability pointers make the generated layout sensitive to PCI capability-chain consistency.

### Per-VF SYSPFVFDEC Indirect MMIO Windows

For `VF0` through `VF23`, the chunk introduces or partially covers `mmBIF_BX_DEV0_EPF0_VF*_MM_INDEX_DEFAULT`, `MM_DATA_DEFAULT`, and `MM_INDEX_HI_DEFAULT`. These reset to zero and represent the per-VF indirect MMIO access window defaults. The companion offset header maps these to per-VF base regions such as the `0xd0400000` style windows seen for later VFs.

### RCC Per-VF Control Defaults

`mmRCC_DEV0_EPF0_VF*_RCC_ERR_LOG_DEFAULT`, `RCC_DOORBELL_APER_EN_DEFAULT`, `RCC_CONFIG_MEMSIZE_DEFAULT`, `RCC_CONFIG_RESERVED_DEFAULT`, and `RCC_IOV_FUNC_IDENTIFIER_DEFAULT` reset to zero for each covered VF. These fields are tied to error logging, doorbell aperture enablement, reported memory size/configuration, reserved config state, and SR-IOV function identification.

The generated `amdgpu/nbio_v2_3.c` consumer uses the non-VF/PF versions of the same NBIO register families for memory size reads and doorbell aperture control, so these VF defaults document the reset baseline for the corresponding virtualized control surfaces.

### BIF Per-VF Doorbell, HDP Flush, Mailbox, and Transaction Defaults

Each complete per-VF `BIFPFVFDEC1` block includes:

- `BIF_BME_STATUS_DEFAULT` and `BIF_ATOMIC_ERR_LOG_DEFAULT`, both zero.
- `DOORBELL_SELFRING_GPA_APER_BASE_HIGH/LOW_DEFAULT`, both zero.
- `DOORBELL_SELFRING_GPA_APER_CNTL_DEFAULT` as `0x00000100`.
- `HDP_REG_COHERENCY_FLUSH_CNTL_DEFAULT`, `HDP_MEM_COHERENCY_FLUSH_CNTL_DEFAULT`, `GPU_HDP_FLUSH_REQ_DEFAULT`, and `GPU_HDP_FLUSH_DONE_DEFAULT`, all zero.
- `BIF_TRANS_PENDING_DEFAULT` and `NBIF_GFX_ADDR_LUT_BYPASS_DEFAULT`, both zero.
- Four transmit mailbox data words, four receive mailbox data words, `MAILBOX_CONTROL_DEFAULT`, `MAILBOX_INT_CNTL_DEFAULT`, and `BIF_VMHV_MAILBOX_DEFAULT`, all zero.

This mirrors active NBIO 2.3 driver responsibilities: `nbio_v2_3_remap_hdp_registers()` remaps HDP flush controls, `nbio_v2_3_enable_doorbell_selfring_aperture()` writes the PF self-ring doorbell aperture base/control fields, and other NBIO paths use mailbox, interrupt, and transaction status registers in the same generated namespace.

### RCC GFX MSI-X Defaults

For complete `BIFDEC2` per-VF blocks, `mmRCC_DEV0_EPF0_VF*_GFXMSIX_VECT0..3_*_DEFAULT` define four MSI-X vector slots. Address-low, address-high, and message-data defaults are zero; each vector `CONTROL_DEFAULT` is `0x00000001`; and `GFXMSIX_PBA_DEFAULT` is zero.

That reset state means vector address/data are unprogrammed, while the control field begins in the generated default state indicated by bit 0. Software that enables interrupts must program address/data and honor the control-mask semantics from the paired shift/mask definitions and PCI MSI-X rules.

## Control Flow and State Behavior

There is no runtime control flow in this header. The only "execution" effect is compile-time macro substitution when AMDGPU code includes the NBIO 2.3 generated headers.

The state represented here is persistent hardware register state after reset or when comparing against expected defaults. Important state categories are:

- SR-IOV VF PCI identity and capability-chain defaults.
- PCIe device/link/MSI/AER/ATS/ARI capability defaults for each virtual function.
- Per-VF indirect MMIO index/data reset state.
- Per-VF RCC doorbell aperture, memory-size/configuration, error-log, and IOV identifier reset state.
- Per-VF BIF bus-master/atomic status, self-ring doorbell GPA aperture state, HDP flush request/done state, transaction-pending state, and mailbox buffers/control.
- Per-VF GFX MSI-X table and pending-bit-array defaults.

Many of these registers are not normal durable software configuration. PCI config command/status fields, AER status logs, HDP flush request/done bits, transaction-pending bits, mailbox buffers, and MSI-X vectors are runtime stateful interfaces. The default macros do not encode ordering, polling, timeout, locking, guest/host ownership, or clear-on-write semantics.

## Dependencies and Integration Points

This chunk belongs to a generated NBIO header set:

- `nbio_2_3_offset.h` supplies matching register addresses and base indices for the names in this default header.
- `nbio_2_3_sh_mask.h` supplies matching bitfield shifts and masks used by `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15`.
- `amdgpu/nbio_v2_3.c` includes `nbio_2_3_default.h`, `nbio_2_3_offset.h`, and `nbio_2_3_sh_mask.h`, and uses the NBIO 2.3 namespace through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, and `WREG32_FIELD15`.
- Linux PCI/SR-IOV and AMDGPU virtualization paths depend on these generated register names matching the hardware and firmware contract for virtual functions.

The active NBIO 2.3 driver code around this namespace handles revision ID reads, memory-controller access enablement, memory-size reads, SDMA/VCN/IH doorbell ranges, doorbell aperture enablement, self-ring aperture programming, HDP flush remapping, interrupt control, and NBIO clock/power gating. This chunk's VF defaults document the reset baseline for related per-VF hardware surfaces even though the chunk itself does not implement those operations.

## Risks

- Generated macro drift is high impact. Wrong defaults for PCI config-space capability pointers can break the VF capability chain seen by the host or guest.
- SR-IOV repetition is easy to damage mechanically. `VF10` through `VF30` config blocks are structurally identical; a one-off rename, value change, or missing macro can affect only one VF and be hard to detect without enumerating many VFs.
- Capability defaults are security and compatibility sensitive. MSI/MSI-X, AER, ATS, and ARI defaults influence interrupt setup, PCIe error handling, address translation behavior, and guest-visible device features.
- Doorbell aperture defaults affect queue submission isolation. Incorrect reset values for `RCC_DOORBELL_APER_EN` or self-ring GPA aperture controls can expose, hide, or misroute doorbell writes in virtualized environments.
- HDP flush defaults are coherency-sensitive. Incorrect request/done/control defaults can make CPU/GPU visibility bugs appear as sporadic memory corruption or hangs.
- Mailbox defaults are virtualization-sensitive. VF-to-host or VF-to-hypervisor mailbox registers must start cleanly; stale nonzero defaults could confuse reset, FLR, or guest-driver initialization flows.
- MSI-X vector-control defaults must stay aligned with hardware semantics. An incorrect default could expose vectors before address/data are programmed or leave interrupts masked when the driver expects otherwise.
- This chunk ends mid-family. The `VF23` per-VF MMIO block continues after line 11799, so final per-file analysis must merge later chunks before claiming complete `VF23` coverage.

## Test and Validation Signals

Useful validation is mostly build, enumeration, virtualization, and hardware bring-up coverage:

- Build AMDGPU code that includes `nbio/nbio_2_3_default.h`; this catches missing or renamed generated macros at compile time.
- Boot an NBIO 2.3 ASIC and verify `amdgpu/nbio_v2_3.c` still reads/writes matching NBIO registers for revision ID, memory size, doorbell aperture setup, HDP remap, and interrupt control.
- Enable SR-IOV and enumerate VFs beyond `VF9`, especially `VF10` through `VF30`, checking PCI config headers, capability chains, MSI/MSI-X capability visibility, AER/ATS/ARI capability layout, and BAR/ROM defaults.
- Exercise guest VF reset/FLR paths and confirm RCC, BIF, mailbox, transaction-pending, HDP flush, and MSI-X state returns to expected defaults.
- Run doorbell submission tests for PF and VF queues, including SDMA/VCN/IH paths, to detect aperture or self-ring default regressions.
- Run interrupt tests with MSI/MSI-X enabled and disabled, verifying vector programming, vector masking, PBA state, and interrupt delivery after VF reset.
- Run GPU memory coherency and HDP flush stress tests across host and guest contexts to catch incorrect flush-control or flush-done expectations.
- Run PCIe AER and virtualization fault-injection tests where available to validate error-log defaults, AER capability visibility, and mailbox/error-reporting behavior.

## Unresolved Cross-Chunk References

Line 8701 starts immediately after the `VF9` PCI config block; the `VF10` address-block comment is at line 8700 just outside the requested range. Line 11799 stops inside `nbio_nbif0_bif_bx_dev0_epf0_vf23_BIFPFVFDEC1`; the remaining `VF23` BIF mailbox fields and later RCC MSI-X defaults continue in a later chunk. The merge/reconciliation lane should stitch those boundaries before producing the final source-file report.
