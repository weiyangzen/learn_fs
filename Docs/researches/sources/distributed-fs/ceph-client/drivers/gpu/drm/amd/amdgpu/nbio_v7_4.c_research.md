# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c

## Purpose
`nbio_v7_4.c` implements NBIO 7.4 support for Arcturus/Aldebaran-class devices. It includes doorbell setup for many SDMA instances, VCN doorbells with Aldebaran offset variants, HDP flush mapping, BIF light sleep, ASPM/LTR programming, BACO dummy-mode cleanup, doorbell interrupt control, and the most complete RAS controller/ATHUB handling in this subset.

## Important APIs, Types, And Functions
Exports are `nbio_v7_4_hdp_flush_reg`, `nbio_v7_4_funcs`, `nbio_v7_4_ras_hw_ops`, and `nbio_v7_4_ras`. Key functions include `nbio_v7_4_sdma_doorbell_range()`, `vcn_doorbell_range()`, `handle_ras_controller_intr_no_bifring()`, `handle_ras_err_event_athub_intr_no_bifring()`, `query_ras_error_count()`, `enable_doorbell_interrupt()`, `program_aspm()`, and `set_reg_remap()`.

## Control Flow
Common init configures NBIO registers, clears BACO dummy enable for NBIO `7.4.4`, remaps HDP registers, and enables doorbells. SDMA doorbell register selection handles non-consecutive SDMA2-7 ranges and an Aldebaran SDMA4 offset. RAS initialization registers controller and ATHUB interrupt IDs; because the BIF ring is disabled, real handling polls doorbell interrupt status, clears it, updates RAS counters, emits logs, and calls the global RAS ISR.

## State And Persistence
The file updates NBIO, PCIe SMN, Aldebaran-specific BIF registers, RAS manager counters, and `adev->nbio` IRQ source descriptors. RAS error counts accumulate in kernel state, while hardware status is cleared after handling.

## Dependencies And Integration Points
It depends on generated NBIO 7.4 headers, local Aldebaran register aliases, `amdgpu_ras`, `amdgpu_irq_add_id()`, SOC15 BIF client IDs, PCIe ASPM support, and KFD remap constants.

## Risks
Aldebaran conditional paths are numerous and easy to regress. RAS status clearing and EOI writes are ordering-sensitive. Some code in this snapshot shows duplicated lines around the Aldebaran interrupt-control read, which should be compared against upstream before modifying.

## Test Signals
RAS injection/query tests, repeated ATHUB/controller interrupt clearing, SDMA0-7 doorbells, Aldebaran VCN/SDMA offset tests, BACO reset paths, ASPM behavior, and HDP flush validation are the main signals.
