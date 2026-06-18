# sources/distributed-fs/ceph-client/include/uapi/cxl/features.h

## Purpose
Defines UAPI payloads for CXL mailbox feature discovery, feature reads, and feature writes following CXL 3.2 command definitions.

## Important APIs, Types, And Functions
Exports `__uapi_uuid_t`, `struct cxl_mbox_get_sup_feats_in`, feature effect flags, `struct cxl_feat_entry`, feature flags, `struct cxl_mbox_get_sup_feats_out`, `struct cxl_mbox_get_feat_in`, `enum cxl_get_feat_selection`, `struct cxl_mbox_set_feat_in`, `enum cxl_set_feat_flag_data_transfer`, and set-feature masks.

## Control Flow
No runtime flow. Kernel builds replace `__uapi_uuid_t` with `uuid_t` after a size assertion. Structures use packed layout, flexible arrays, `__struct_group`, and counted-by annotations.

## State, Persistence, And Dependencies
Mailbox payloads represent device feature state. Set-feature flags describe whether changes are current, default, saved, reset-persistent, or require reset/background effects. It depends on `<linux/types.h>` plus kernel-only `<linux/uuid.h>`.

## Integration Points
Used by CXL memory-device mailbox command handling, user tools issuing CXL ioctl/mailbox commands, firmware feature negotiation, and management daemons.

## Risks
Packed layout and UUID alignment are critical. Reserved fields must be zero. Multi-part set transfers need offset/version/abort semantics handled carefully. Effects flags inform reset and persistence behavior, so misreporting them can cause unsafe configuration changes.

## Test Signals
UAPI size/offset tests, mailbox encode/decode tests against CXL 3.2 tables, reserved-zero validation, UUID alignment checks, multi-transfer set-feature tests, and feature persistence/reset behavior tests.
