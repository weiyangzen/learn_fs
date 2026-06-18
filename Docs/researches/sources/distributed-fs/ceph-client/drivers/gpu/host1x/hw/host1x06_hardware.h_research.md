<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x06_hardware.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x06_hardware.h

## Purpose

`host1x06_hardware.h` is the hardware-register umbrella header for host1x06 (Tegra186). It gathers the generated register/field definitions and opcode helpers needed by the shared hardware implementation files.

## Important APIs, Types, And Functions

- Includes `hw_host1x06_channel.h`, `hw_host1x06_uclass.h`, `hw_host1x06_vm.h`, `hw_host1x06_hypervisor.h`, and `opcodes.h`.
- Provides the register macros consumed by `cdma_hw.c`, `channel_hw.c`, `debug_hw.c`, `intr_hw.c`, and `syncpt_hw.c`.
- Layout focus: VM channel/sync registers plus hypervisor protection and FIFO-peek registers.
- SoC capability context: 63 channels, 576 syncpoints, 24 mlocks, wide gathers, 40-bit DMA, hypervisor registers, stream-ID protection.

## Control Flow

There is no runtime control flow. The inclusion order determines which register names and field helpers are visible when the generation `.c` file includes shared hardware code.

## State And Persistence Behavior

No software state is stored. The macros describe hardware state that persists in MMIO registers after writes from the host1x driver.

## Dependencies And Integration Points

It depends on Linux type/bit helpers and the generated host1x register headers. It is included only through the matching `host1x06.c` generation unit.

## Risks And Test Signals

Omitting a register header causes compile failures; wrong offsets cause silent hardware misprogramming. Test signals include generation-specific build coverage, probe, channel DMA, syncpoint interrupts, debugfs dumps, and timeout recovery on Tegra186.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/host1x06_hardware.h -->
