# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn20k.h

## Purpose

`cn20k.h` declares CN20K-specific NIC entry points used by common PF/VF and TC code. It is a narrow header for hardware-op installation, PF/VF mailbox interrupt management, and TC MCAM priority helpers.

## Important APIs, Types, And Functions

- Forward declarations for `struct otx2_flow_config` and `struct otx2_tc_flow`.
- `cn20k_init()` installs CN20K `dev_hw_ops`.
- `cn20k_register_pfvf_mbox_intr()`, `cn20k_disable_pfvf_mbox_intr()`, and `cn20k_enable_pfvf_mbox_intr()` manage PF/VF mailbox interrupts.
- `cn20k_tc_update_mcam_table_del_req()`, `cn20k_tc_update_mcam_table_add_req()`, `cn20k_tc_alloc_entry()`, and `cn20k_tc_free_mcam_entry()` manage CN20K TC MCAM entries.

## Control Flow

There is no executable control flow in this header. Callers use these prototypes to dispatch CN20K-specific setup from probe and to call CN20K TC helpers when installing/removing flower rules.

## State And Persistence

No state is stored here. Implementations mutate NIC runtime state, IRQ registrations, TC flow lists, and hardware MCAM contexts.

## Dependencies And Integration Points

It includes `otx2_common.h`, so it shares core NIC types and also relies on include guards to avoid recursive header issues. It is included by common NIC and TC code that needs CN20K specialization.

## Risks

- Prototype drift breaks cross-file builds.
- The `cn20k_tc_alloc_entry()` parameter name `dummy` hides that callers pass an install-flow request; mismatched expectations can obscure review.
- Including `otx2_common.h` from a silicon-specific header increases rebuild/blast radius for common header changes.

## Test Signals

Build coverage with CN20K support enabled and disabled, plus probe and TC offload tests that call every declared function, validate this header.
