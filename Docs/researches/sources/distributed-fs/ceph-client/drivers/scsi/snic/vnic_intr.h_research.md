## sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_intr.h

### Purpose
Defines the Cisco SNIC vNIC interrupt-control register layout and small inline helpers used by the SNIC interrupt path to mask, unmask, and return interrupt credits to hardware. The file is a hardware ABI header: `struct vnic_intr_ctrl` mirrors the memory-mapped interrupt control table, while `struct vnic_intr` binds a software index and `struct vnic_dev` to that MMIO block.

### Important APIs, Types, and Constants
- `VNIC_INTR_TIMER_MAX`, `VNIC_INTR_TIMER_TYPE_ABS`, and `VNIC_INTR_TIMER_TYPE_QUIET` constrain interrupt coalescing timer programming.
- `struct vnic_intr_ctrl` exposes register offsets for `coalescing_timer`, `coalescing_value`, `coalescing_type`, `mask_on_assertion`, `mask`, `int_credits`, and `int_credit_return`.
- `struct vnic_intr` stores the interrupt index, owning `vnic_dev`, and `ctrl` MMIO pointer.
- Inline APIs `svnic_intr_mask()`, `svnic_intr_unmask()`, `svnic_intr_credits()`, `svnic_intr_return_credits()`, and `svnic_intr_return_all_credits()` are the hot-path helpers.
- Out-of-line lifecycle functions `svnic_intr_alloc()`, `svnic_intr_init()`, `svnic_intr_clean()`, and `svnic_intr_free()` are implemented elsewhere.

### Control Flow and State
The interrupt handler path reads `int_credits`, combines returned credits with optional unmask and timer-reset bits in `svnic_intr_return_credits()`, and writes `int_credit_return`. `svnic_intr_return_all_credits()` is a convenience wrapper that reads the current credit count and returns all credits while unmasking and resetting the timer. Masking state is held in hardware via the MMIO `mask` register rather than in software.

### Dependencies and Integration Points
The header depends on Linux PCI/MMIO helpers and `vnic_dev.h`. SNIC ISR code calls these helpers after completion queue servicing, especially MSI-X handlers that return completion credits. Correctness depends on the register layout matching firmware/hardware expectations.

### Risks and Test Signals
Risk concentrates around MMIO ordering and bit packing: the credit field is 16 bits, with unmask at bit 16 and reset timer at bit 17. Tests should exercise ISR credit return, interrupt coalescing configuration, and sustained completion load to catch lost interrupts, stuck masks, or coalescing timer regressions.
