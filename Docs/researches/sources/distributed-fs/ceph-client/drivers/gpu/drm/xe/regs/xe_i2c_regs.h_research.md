# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_i2c_regs.h

## Purpose

`xe_i2c_regs.h` defines SoC-relative register offsets for the Xe I2C bridge, its PCI config-space aperture, memory-space aperture, SG remap address registers, and bridge interrupt/power-management control.

## Important APIs, Types, and Definitions

- Address bases: `I2C_BRIDGE_OFFSET`, `I2C_CONFIG_SPACE_OFFSET`, and `I2C_MEM_SPACE_OFFSET`, all based on `SOC_BASE`.
- Remapper registers: `REG_SG_REMAP_ADDR_PREFIX` and `REG_SG_REMAP_ADDR_POSTFIX`.
- Bridge/config registers: `I2C_BRIDGE_PCICFGCTL`, `ACPI_INTR_EN`, `I2C_CONFIG_CMD`, and `I2C_CONFIG_PMCSR`.

## Control Flow

This header has no local control flow. I2C bridge code uses the offsets to configure PCI command and PMCSR state, enable ACPI interrupts, and program remap state before accessing bridge memory/config spaces.

## State and Persistence Behavior

The state is SoC/bridge MMIO and PCI-config shadow state. Configuration persists until the device or bridge is reset, suspended, or reconfigured. Remap prefix/postfix state affects how subsequent accesses are routed.

## Dependencies and Integration Points

It depends on `<linux/pci_regs.h>` for PCI config offsets, `xe_reg_defs.h` for register construction, and `xe_regs.h` for `SOC_BASE`. It integrates with Xe display/I2C bridge bring-up and platform-specific SoC remapping paths.

## Risks and Edge Cases

- The file mixes SoC MMIO offsets and PCI config offsets; consumers must use the correct access path.
- `SOC_BASE` drift affects all derived addresses.
- Incorrect remap programming can make later I2C accesses target the wrong region.

## Test Signals

Useful signals include successful I2C bridge enumeration, PCI command/PMCSR programming, ACPI interrupt enable behavior, and platform display/I2C probing on SoCs using these bridge windows.
