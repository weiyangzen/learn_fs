# sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnetconfig_lnd.c

## Purpose
`liblnetconfig_lnd.c` implements the LND-specific tunable serialization and YAML extraction functions declared in `liblnd.h`. It keeps driver-specific fields out of the main LNet configuration implementation while allowing network show output and YAML config input to carry common and LND-specific tunables.

## Important APIs and Types
- `lustre_net_show_tunables()` emits common network tunables: `peer_timeout`, `peer_credits`, `peer_buffer_credits`, and `credits`.
- `lustre_ni_show_tunables()` dispatches by LND type and emits driver-specific fields for O2IB (`peercredits_hiw`, FMR/cache/send/timeout/TOS fields), EFA (`nqps`), SOCK (`conns_per_peer`, `timeout`, `tos`), optional KFI (`prov_*`, `auth_key`, `traffic_class`, `traffic_class_num`, `timeout`), and optional GNI (`timeout`).
- `lustre_yaml_extract_lnd_tunables()` dispatches by LND type and fills the corresponding union member of `struct lnet_lnd_tunables`.
- Static extraction helpers parse the `lnd tunables` YAML object and apply per-driver defaults for absent fields.

## Control Flow
Show helpers are linear serializers: each field calls `cYAML_create_number()` or `cYAML_create_string()` and returns `LUSTRE_CFG_RC_OUT_OF_MEM` on the first allocation failure. `lustre_ni_show_tunables()` chooses the helper based on `net_type`, with KFI and GNI branches included only when compile-time macros enable them.

YAML extraction helpers first locate the `lnd tunables` child object. If absent, they return `false` so the caller can distinguish "no LND tunables supplied" from supplied values. Present fields are copied from `cy_valueint` or `cy_valuestring`; absent fields get defaults such as O2IB `map_on_demand = UINT_MAX`, O2IB/SOCK `conns_per_peer = 1`, TOS `-1`, and most other numeric fields `0`. KFI string extraction copies `traffic_class` only if it is present and shorter than `LNET_MAX_STR_LEN`.

## State and Persistence
The file stores no global state. It only mutates caller-provided YAML trees or tunable structs. Persistence occurs later when `liblnetconfig.c` copies the populated `struct lnet_ioctl_config_lnd_tunables` into NI configuration ioctl payloads, or when show output is saved as backup YAML.

## Dependencies and Integration Points
It depends on `liblnd.h`, `liblnetconfig.h`, `cyaml`, libc/limits utilities, and LNet UAPI tunable structs. It is called from `liblnetconfig.c` during `lustre_lnet_show_net()` and YAML NI/ip2nets configuration. Compile-time integration depends on `HAVE_KFILND` and `HAVE_GNILND`.

## Risks and Edge Cases
Extraction does not perform numeric range validation; invalid or out-of-range values are left for later kernel/ioctl validation. Missing `lnd tunables` returns false even if common tunables are present, which is intentional but requires the caller to combine masks correctly. Backup mode suppresses KFI `traffic_class_num`, so backup YAML preserves the string-oriented configuration rather than runtime numeric detail. String copying for KFI traffic class avoids overflow by length check but silently leaves the field unchanged/default when the string is too long. Unsupported LND types produce no-match/false rather than hard errors.

## Test Signals
Tests should cover successful show output for each compiled LND, allocation failure on each emitted field, YAML extraction defaults for absent fields, KFI traffic-class length behavior, backup vs non-backup KFI output, unsupported LND return behavior, and integration with `liblnetconfig.c` tunable inheritance from network-level YAML to local NI entries.
