# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c

## Purpose
`nbio_v7_9.c` implements a multi-AID NBIO 7.9 backend for newer datacenter parts. Beyond standard NBIO services, it routes SDMA and VCN doorbells through per-AID S2A entries, exposes compute and memory partition mode queries, detects NPS switch requests, manages XCC doorbell fences, clears BACO dummy state per AID, controls doorbell interrupt masking, and registers RAS controller/ATHUB handlers.

## Important APIs, Types, And Functions
Exports are `nbio_v7_9_hdp_flush_reg`, `nbio_v7_9_funcs`, `nbio_v7_9_ras_hw_ops`, and `nbio_v7_9_ras`. Key functions include `sdma_doorbell_range()`, `vcn_doorbell_range()`, `get_compute_partition_mode()`, `get_memory_partition_mode()`, `is_nps_switch_requested()`, `init_registers()`, `enable_doorbell_interrupt()`, and the RAS no-BIF-ring handlers.

## Control Flow
SDMA doorbell setup maps the SDMA device instance to an AID and per-AID instance slot, then writes both range entries and S2A port control with distinct AWID/range/address values. VCN doorbells choose range size by GC IP and add a fence bit for nonzero AIDs. Init programs XCC doorbell fences, GFX interrupt monitor masks, per-AID SHUB slave-mode fences, and clears BACO dummy enable when not in SR-IOV. Partition queries read NBIO partition status/capability registers.

## State And Persistence
State spans per-AID NBIO extended registers, `adev->sdma.instance[].aid_id`, `adev->aid_mask`, `adev->gfx.xcc_mask`, partition status registers, and RAS manager counters. It is hardware/runtime state, not persistent storage.

## Dependencies And Integration Points
It depends on generated NBIO 7.9 headers, BIF interrupt IDs, `amdgpu_ras`, SDMA instance metadata, XCC/AID topology helpers, KFD remap constants, and common NBIO dispatch.

## Risks
Multi-AID routing depends on correct topology metadata; wrong `aid_id` or `num_inst_per_aid` sends doorbells to the wrong engine. Clock-gating callbacks are intentionally empty. `query_ras_error_count()` is empty, so RAS controller interrupts log but cannot harvest counts. The snapshot includes duplicated text in the doorbell aperture write, which should be checked before editing.

## Test Signals
Exercise SDMA instances across AIDs, VCN on multiple AIDs, XCC doorbell fences, partition mode sysfs/ioctl consumers, NPS switch status, RAS interrupt registration/clear paths, and BACO dummy cleanup.
