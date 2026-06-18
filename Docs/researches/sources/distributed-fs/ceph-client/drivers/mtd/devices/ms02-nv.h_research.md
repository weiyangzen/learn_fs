# sources/distributed-fs/ceph-client/drivers/mtd/devices/ms02-nv.h

Purpose: hardware description for the DEC MS02-NV NVRAM module. It documents the decoded SRAM/CSR layout, firmware-reserved diagnostic ranges, battery LED/CSR semantics, and the private state shared with `ms02-nv.c`.

Important APIs/types/functions: exports register/memory offsets such as `MS02NV_CSR`, `MS02NV_DIAG`, `MS02NV_MAGIC`, `MS02NV_VALID`, and `MS02NV_RAM`; status masks such as `MS02NV_CSR_BATT_OK`, `MS02NV_DIAG_SIZE_MASK`; magic IDs `MS02NV_ID` and `MS02NV_VALID_ID`; `typedef volatile u32 ms02nv_uint`; and `struct ms02nv_private`.

Control flow: the header has no executable flow, but its constants drive probe validation, size calculation, and user-region alignment in the C file. `MS02NV_RAM` is the policy boundary that excludes firmware diagnostic and validity data from the MTD.

State and persistence: `struct ms02nv_private` stores the MTD linked-list pointer, owned `struct resource` handles for module/diagnostic/user/CSR areas, full physical mapping pointer, detected size, and exposed user pointer. The constants describe persistent firmware status and battery-backed RAM content.

Dependencies/integration: includes Linux `ioport` and MTD declarations and relies on u32 types from the including compilation environment. It is private to the MS02-NV driver, not a public kernel API.

Risks: comments document a critical firmware behavior: corrupting the valid-data word area can cause firmware to disable battery backup and erase data on power-off. The C file mitigates this by exposing only page-aligned RAM starting at `0x1000`.

Test signals: code using this header should probe `MS02NV_MAGIC == MS02NV_ID`, cap detected RAM before `MS02NV_CSR`, and never expose offsets below `MS02NV_RAM` through normal MTD access.
