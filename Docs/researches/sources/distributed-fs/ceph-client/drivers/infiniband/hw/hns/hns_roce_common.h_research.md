# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_common.h

Purpose: Provides low-level MMIO access helpers, endian-safe register/descriptor field macros, and register offset definitions used by HNS RoCE hardware code.

Important APIs/types/functions: `roce_write()`, `roce_read()`, and `roce_raw_write()` wrap MMIO. `roce_get_field()`, `roce_set_field()`, `roce_get_bit()`, and `roce_set_bit()` operate on little-endian 32-bit values. `FIELD_LOC` plus `hr_reg_*` macros encode typed bitfield locations and perform compile-time checks where fields must stay inside one dword.

Control flow: Hardware-specific code uses these macros while building context descriptors and touching MMIO registers. Register definitions include vendor/GUID/GID/SMAC, mailbox, doorbell, EQ, ECC, CMQ, VF interrupt, and extended doorbell registers.

State and persistence: No independent runtime state. The constants define the persistent hardware register map assumed by the driver.

Dependencies and integration: Depends on Linux bitfield helpers and MMIO APIs. Included by command, CQ, HEM, and hardware v2 code.

Risks: Field macros use pointer casting to `__le32 *`; callers must pass correctly laid-out packed hardware descriptors. Cross-dword field misuse is intentionally caught in some helpers. Register offset drift against hardware revisions is high risk. Test signals include compile-time field checks, hardware init/readback tests, sparse/endian analysis, and register-level failure injection around mailbox and EQ paths.
