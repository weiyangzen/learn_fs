# sources/distributed-fs/lustre-release/lnet/utils/lnetconfig/liblnd.h

## Purpose
`liblnd.h` is the small public header for LNet Driver (LND) tunable conversion helpers used by the LNet configuration library. It exposes the bridge between kernel/user-space LND tunable structures and the `cYAML` representation emitted or consumed by `lnetctl` YAML workflows.

## Important APIs and Types
- `lustre_net_show_tunables(struct cYAML *tunables, struct lnet_ioctl_config_lnd_cmn_tunables *cmn)` serializes common network tunables such as peer timeout and credit counts.
- `lustre_ni_show_tunables(struct cYAML *lnd_tunables, __u32 net_type, struct lnet_lnd_tunables *lnd, bool backup)` serializes driver-specific tunables for O2IB, EFA, socket, and conditionally KFI/GNI networks.
- `lustre_yaml_extract_lnd_tunables(struct cYAML *tree, __u32 net_type, struct lnet_lnd_tunables *tun)` parses driver-specific `lnd tunables` YAML back into kernel ioctl tunable structures.
- The header depends on `struct lnet_lnd_tunables`, `struct lnet_ioctl_config_lnd_cmn_tunables`, `__u32`, and `struct cYAML`.

## Control Flow
The header itself has no executable control flow. Callers in `liblnetconfig.c` use these functions while showing network details and while extracting tunables from YAML network or interface blocks. The implementations in `liblnetconfig_lnd.c` dispatch by `net_type`, returning success for supported LNDs, no-match for unsupported show paths, or `false` for unsupported YAML extraction.

## State and Persistence
No state is stored by this header. The API mutates caller-owned `cYAML` trees on show and caller-owned tunable structs on YAML extraction. Persistent behavior occurs only after `liblnetconfig.c` later sends the populated structures to LNet kernel ioctls.

## Dependencies and Integration Points
This file includes Linux LNet UAPI headers, `socklnd` definitions, and `cyaml.h`. It integrates with `liblnetconfig.c` network show/configuration paths and with `liblnetconfig_lnd.c`, which provides the concrete serialization/extraction logic.

## Risks and Edge Cases
The API trusts callers to pass a valid `net_type` and correctly sized tunable union. Unsupported or conditionally compiled LNDs are intentionally absent at runtime, so callers must treat no-match/false as non-fatal when a network type has no user-space tunables. `backup` output can omit fields that are useful for inspection but not necessary or desirable for reconfiguration.

## Test Signals
Useful tests should verify show/extract round trips for each built LND, no-match handling for unsupported LNDs, backup-mode omission behavior, and null-allocation failure propagation through `cYAML_create_*` return checks in the implementation.
