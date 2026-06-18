# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_cccb.h

Purpose: declares the client CCB structure and helper API for queue command submission.

Important APIs/types: `struct pvr_cccb` stores firmware objects, control/data CPU mappings, firmware addresses, ring size, local write offset, and wrap mask. `PADDING_COMMAND_SIZE` names the firmware padding header size. Helpers include init/fini, command write, single/combined KCCB kicks, `pvr_cccb_cmdseq_fits()`, `pvr_cccb_get_size_of_cmd_with_hdr()`, and `pvr_cccb_cmdseq_can_fit()`.

Control flow and state: queue code computes command sequence size, checks whether it can ever fit and currently fits, writes commands, then kicks firmware using reserved KCCB capacity.

Dependencies and integration: includes Rogue firmware ABI headers and forward declares PowerVR device, firmware object, and HWRT data structures.

Risks: `pvr_cccb_get_size_of_cmd_with_hdr()` warns on unaligned command sizes, so callers must pre-align firmware payload contracts. The half-capacity policy in `cmdseq_can_fit()` is a simplifying invariant used by fencing logic.

Test signals: compile/runtime coverage from job queue submission, especially ring wrap and combined geometry/fragment jobs.
