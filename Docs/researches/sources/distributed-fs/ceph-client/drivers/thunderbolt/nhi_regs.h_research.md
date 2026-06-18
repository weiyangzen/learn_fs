<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_regs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_regs.h` defines the MMIO and PCI VSEC register contract for NHI rings, interrupts, mailbox, reset, firmware status, and Ice Lake link-controller registers. The source was read as a complete 179-line file.

## Important APIs, Types, and Functions

Important definitions include `enum ring_flags`, packed `struct ring_desc`, TX/RX ring base offsets, TX/RX options bases, interrupt notify/mask/clear bases, vector allocation fields, interrupt throttling, `REG_CAPS`, `REG_DMA_MISC`, `REG_RESET`, in/out mailbox registers, firmware status bits, Ice Lake VSEC offsets `VS_CAP_9` through `VS_CAP_22`, and `enum icl_lc_mailbox_cmd`.

## Control Flow

There is no runtime flow in this header. `nhi.c` uses the register constants to program ring descriptors, enable/disable interrupts, allocate MSI-X vectors, read firmware mode, issue mailbox commands, and reset host routers. `nhi_ops.c` uses the VSEC constants for force-power, firmware-ready, LTR, and LC mailbox sequences.

## State and Persistence Behavior

The file describes hardware state. Ring descriptor base/head/tail/count registers, options registers, interrupt status/mask registers, and mailbox bits reflect live controller state. The packed descriptor layout is DMA-visible and must match hardware.

## Dependencies and Integration Points

It includes `<linux/types.h>` and assumes bit helpers such as `BIT()`, `GENMASK()`, and `FIELD_GET()` are available through the wider kernel include context. It depends on `enum ring_desc_flags` being visible through included Thunderbolt headers when `struct ring_desc` is used. It is tightly coupled to NHI hardware documentation and the register accessors in `nhi.c`.

## Risks and Edge Cases

Wrong bit positions or offsets can corrupt DMA rings, mask the wrong interrupt, or wedge firmware mailbox commands. `RING_NOTIFY_REG_COUNT()` and `RING_INTERRUPT_REG_COUNT()` depend on `nhi->hop_count`; off-by-one errors would skip status words. The packed bitfield descriptor has compiler/ABI sensitivity but is in kernel style for this hardware interface.

## Test Signals

Build coverage on supported architectures, ring bring-up on hardware with different hop counts, MSI-X vector allocation readback, mailbox command success/failure paths, host reset on v2+ routers, and Ice Lake force-power/LTR PM tests validate this register contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/nhi_regs.h -->
