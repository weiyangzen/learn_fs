<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/hw-ish-regs.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/hw-ish-regs.h

## Purpose
`hw-ish-regs.h` defines the Intel ISH IPC register map, bit fields, doorbell header encoding, firmware status values, protocol IDs, and management command IDs used by the ISH hardware IPC layer.

## Important APIs, Types, and Functions
Register offsets cover interrupt status/mask, firmware status, host communication, reset, host-to-ISH and ISH-to-host doorbells, message windows, and DMA remap enable. Bit macros define busy bits, host ownership, host ready/ILUP, interrupt enables for Cherry Trail versus Broxton-style hardware, firmware ready/DMA bits, and DMA enable. Header helpers include `IPC_HEADER_GET_LENGTH`, `IPC_HEADER_GET_PROTOCOL`, `IPC_HEADER_GET_MNG_CMD`, `IPC_BUILD_HEADER`, `IPC_BUILD_MNG_MSG`, `IPC_IS_BUSY`, and readiness tests.

## Control Flow
There is no executable flow, but these macros drive `ipc.c`: IRQ handling reads doorbell protocol/length/command, transmit builds doorbell values, reset and clock sync use management commands, and DMA/power handling checks firmware status bits.

## State and Persistence Behavior
The header owns no memory. It names hardware registers whose values persist in the PCI MMIO block and firmware state machine until changed by host, firmware, reset, or power transition.

## Dependencies and Integration Points
It is included by `hw-ish.h` and indirectly by `ipc.c`. It depends on kernel integer types and `GENMASK` availability through surrounding includes. It is the ABI between host driver and ISH firmware/hardware.

## Risks and Edge Cases
Incorrect offsets, masks, or protocol constants break all IPC. The clear macros use XOR to clear bits, so callers must ensure bits are set before using them or risk toggling them on. Platform-specific interrupt bits differ between CHV and later devices; using the wrong path can lose interrupts. Header length masks must match IPC payload limits enforced in the ISR.

## Test Signals
Signals include successful host-ready negotiation, reset-notify exchange, ISHTP message traffic, DMA enable/disable, suspend/resume ACKs, firmware clock sync, and interrupt counters increasing without bad-length drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/hw-ish-regs.h -->
