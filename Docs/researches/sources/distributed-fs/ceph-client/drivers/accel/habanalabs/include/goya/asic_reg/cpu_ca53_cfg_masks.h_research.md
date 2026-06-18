<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_ca53_cfg_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_ca53_cfg_masks.h

## Purpose
Auto-generated bitfield mask and shift definitions for the Goya `CPU_CA53_CFG` register block, which controls ARM Cortex-A53 boot mode, reset release, interrupt inputs, power-management handshakes, debug access, memory attributes, PMU events, and status reporting.

## Important APIs, Types, And Functions
- Boot/config fields cover `ARM_CFG` execution state, endianness, exception target, and high-vector selection.
- Reset address fields define LSB/MSB vector masks for two cores.
- `ARM_RST_CONTROL` masks control CPU, core, L2, debug, MBIST, and warm reset lines.
- `ARM_GIC_IRQ_CFG` masks expose GIC interrupt lines and enable.
- `ARM_PWR_MNG`, `ARM_PWR_STAT_0`, and `ARM_PWR_STAT_1` masks cover Q-channel, WFI/WFE, L2 flush, and debug power handshakes.
- Debug and memory masks cover debug modes/status, debug ROM address, memory attributes, and PMU event fields.

## Control Flow
The header has no executable flow. Goya bring-up and reset code combines these masks with values read from or written to the corresponding `cpu_ca53_cfg_regs.h` offsets. Typical flows set reset vectors, configure core mode, release reset lines, enable GIC behavior, and poll status bits.

## State And Persistence Behavior
The masks describe volatile hardware register fields. State persists in the CPU configuration registers until changed by software or reset. Reset and power status fields reflect hardware state rather than driver-owned persistence.

## Dependencies And Integration Points
Pairs with `cpu_ca53_cfg_regs.h` for register offsets and generated Goya register blocks. Integrates with boot code, low-level reset sequencing, CPU debug enablement, power management, and PMU/debug diagnostics.

## Risks And Edge Cases
Incorrect masks can hold the CPU in reset, boot it from the wrong vector, use the wrong execution state, or break interrupt delivery. Multi-core fields often pack two bits or two lanes in one register, so shifts must be applied precisely. Generated masks should be treated as ASIC source of truth, not hand-edited.

## Test Signals
Signals include successful ARM boot from programmed vectors, reset-release sequencing, GIC interrupt delivery, power-state polling matching hardware behavior, and debug/PMU access functioning when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/cpu_ca53_cfg_masks.h -->
