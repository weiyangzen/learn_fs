# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_fwif.h

## Purpose
Collects host-side GuC firmware interface definitions used by Xe GuC submission, logging, policy, hardware config, engine activity, and page-fault handling.

## Important APIs, Types, And Functions
The header defines G2H message lengths, generic KLV structs, execution-queue policy update packets, GuC control dword fields, global scheduler policy structures, GT system-info and ADS layouts, engine usage/activity records, GuC receive-message bits, UM queue parameters, page-fault descriptors/replies, and access-counter descriptors.

## Control Flow
No executable flow is present. The layouts drive CT/MMIO command construction and parsing elsewhere. For example, `xe_guc_pagefault.c` parses `xe_guc_pagefault_desc` fields and builds `xe_guc_pagefault_reply`; `xe_guc_engine_activity.c` maps GuC activity metadata and records; GuC load code fills control/ADS fields.

## State And Persistence
All structs describe persistent shared memory or wire-format state owned by GuC and the host. Most are `__packed`, making ABI layout stability the central requirement.

## Dependencies And Integration Points
Includes GuC capture, KLV, scheduler ABI headers and engine class types. It is a core integration point between Xe driver code and GuC firmware protocol, including SR-IOV and page-fault UM queue setup.

## Risks And Test Signals
Any field-width, mask, packing, or length mismatch can break firmware communication. Page-fault comments note that some values currently match Xe pagefault enums by coincidence and would need remapping if enums diverge. Test signals are firmware boot success, CT action success, page-fault response handling, engine activity reads, and ABI compile assertions in consumers.
