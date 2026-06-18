<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-capdata.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-capdata.h

## Purpose
This header defines the shared ABI between Lenovo capability-data providers and consumers. It describes support flags, encoded attribute IDs, data record layouts, the binder object used by the component framework, and lookup function prototypes.

## Important APIs, Types, And Functions
`LWMI_SUPP_VALID`, `LWMI_SUPP_GET`, and `LWMI_SUPP_SET` describe attribute validity and access support. The attribute ID is packed with device, feature, mode, and type fields using `LWMI_ATTR_*_MASK`. `lwmi_attr_id()` builds this packed ID using `FIELD_PREP()`. `struct capdata00` carries `id`, `supported`, and `default_value`; `struct capdata01` adds `step`, `min_value`, and `max_value`; `struct capdata_fan` carries fan ID plus min/max RPM. `struct lwmi_cd_binder` carries CD00/CD01 list pointers and an optional callback for Fan Test Data.

## Control Flow
The header has no executable control flow except the inline encoder. Runtime behavior is supplied by `wmi-capdata.c` and consumers such as `wmi-other.c`. The intended flow is: consumer asks `lwmi_cd_match_add_all()` to match capdata components, receives list pointers through `lwmi_cd_binder`, then calls the typed `lwmi_cd*_get_data()` helpers with packed IDs.

## State And Persistence
The header owns no state. It documents pointer lifetime for `cd_fan_list_cb`: the fan list pointer is only valid during the callback and must not be retained by consumers.

## Dependencies And Integration Points
The header depends on Linux bitfield helpers and forward declarations for `device`, `component_match`, and `cd_list`. It is imported by Lenovo WMI capdata and "Other Mode" drivers and is part of the `LENOVO_WMI_CAPDATA` exported namespace.

## Risks And Edge Cases
Incorrectly encoded attribute IDs cause silent lookup failures or wrong feature mapping. Consumers must respect support bits and callback lifetime. The packed ID layout is firmware ABI, so changing masks or field order would break all capdata lookups.

## Test Signals
Tests should verify `lwmi_attr_id()` field packing, support-flag interpretation, consumer handling of missing CD lists, and compile-time integration between `wmi-capdata.c` and `wmi-other.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-capdata.h -->
