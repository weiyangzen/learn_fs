## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_hw_utils.h

Purpose: declarations and small utility macros for Atlantic hardware helpers.

Important APIs/types: defines `LODWORD`, `HIDWORD`, sleep/log macros, forward-declares `struct aq_hw_s`, and declares register access, bit access, descriptor-cache invalidation, error translation, and TC geometry helpers.

Control flow: none.

State and persistence: none.

Dependencies/integration: includes `linux/iopoll.h` and `aq_common.h`; used by hardware generation code and higher-level Atlantic files.

Risks: `AQ_HW_SLEEP(_US_)` maps to `mdelay`, so callers must avoid long delays in inappropriate contexts. Logging macros hardcode the driver name prefix.

Test signals: compile coverage, call-site timing review, and register helper tests through hardware operations.
