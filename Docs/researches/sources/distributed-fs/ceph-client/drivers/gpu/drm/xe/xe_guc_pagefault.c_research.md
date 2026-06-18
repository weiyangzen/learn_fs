# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pagefault.c

## Purpose
Bridges GuC page-fault G2H messages into the generic Xe pagefault layer and sends GuC page-fault response descriptors.

## Important APIs, Types, And Functions
Exports `xe_guc_pagefault_handler`. Internal `guc_ack_fault` implements `struct xe_pagefault_ops.ack_fault` by building `XE_GUC_ACTION_PAGE_FAULT_RES_DESC` and sending it through the GuC CT.

## Control Flow
The handler validates the message length against `struct xe_guc_pagefault_desc`, populates `xe_pagefault.consumer` fields from GuC bitfields, handles Xe2 TRVA faults as NACKs, stores the original producer message and GuC private pointer, then calls `xe_pagefault_handler`. When the generic layer acknowledges, `guc_ack_fault` reconstructs ASID, VFID, prefetch, engine, and private data fields and sends a response descriptor.

## State And Persistence
The function uses a stack `struct xe_pagefault`; persistence is limited to the original GuC message copied into the producer buffer for later ack construction.

## Dependencies And Integration Points
Depends on GuC action/page-fault ABI masks from `xe_guc_fwif.h`, `xe_guc_ct_send`, and the generic `xe_pagefault` subsystem. It integrates GuC UM page-fault producer data with host VM fault resolution.

## Risks And Test Signals
The code comments note that GuC values currently match Xe pagefault enums and require remapping if that changes. The `PFR_SUCCESS` bit is derived from `!!err`, which is a semantic hotspot worth checking against firmware ABI expectations. Tests should cover exact length validation, TRVA/NACK mapping, prefetch handling, and CT response contents for success and failure paths.
