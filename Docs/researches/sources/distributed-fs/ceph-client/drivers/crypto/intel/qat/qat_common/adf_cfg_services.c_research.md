# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_services.c

## Purpose
This file parses and normalizes QAT `ServicesEnabled` configuration values, converts service strings to bitmasks and back, reports composed service modes, and checks whether a base service is active in the ring-to-service map.

## Important APIs, Types, And Functions
Public APIs are `adf_parse_service_string()`, `adf_get_service_mask()`, `adf_get_service_enabled()`, `adf_srv_to_cfg_svc_type()`, and `adf_is_service_enabled()`. Internal helpers are `adf_service_string_to_mask()` and `adf_service_mask_to_string()`. The string table maps `SVC_ASYM`, `SVC_SYM`, `SVC_DC`, `SVC_DCC`, and `SVC_DECOMP` to config strings.

## Control Flow
Parsing copies the input into a fixed buffer, splits on `;`, matches known service strings, rejects duplicates, rejects too many services, and asks hardware data's `services_supported()` callback when present. Mask-to-string reserializes in enum order. `adf_get_service_enabled()` maps parsed masks to composed service identifiers such as `SVC_SYM_ASYM`, `SVC_SYM_DC`, or `SVC_ASYM_DC`; otherwise it returns the single service.

## State And Persistence Behavior
No long-lived state is stored here. It reads volatile config from `accel_dev->cfg` and returns transient masks or normalized strings.

## Dependencies And Integration Points
It depends on config storage, service string constants, hardware-data service support callbacks, and ring-to-service maps in `hw_data`. Gen4/Gen6 capability and firmware selection depend on its outputs.

## Risks
Service enum order affects normalized strings and composed-mode selection. `SVC_DCC` is extended and excluded from some multi-service mixes by hardware callbacks. Empty masks are rejected only in the public parse path.

## Test Signals
Valid/invalid service strings, duplicate tokens, too many tokens, hardware unsupported masks, Gen6 WCY rejection, ring-to-service active checks, and capability/firmware selection for each service mix.
