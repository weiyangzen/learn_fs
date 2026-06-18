# sources/distributed-fs/ceph-client/Documentation/netlink/specs/psp.yaml

Purpose: this YAML defines the PSP Security Protocol generic-netlink family used to discover PSP-capable devices, configure accepted protocol versions, rotate device keys, bind Rx/Tx associations to sockets, and read PSP statistics.

Important APIs, types, and functions: the `version` enum distinguishes AES-GCM and AES-GMAC variants with 128-bit or 256-bit keys. Attribute set `dev` exposes `id`, `ifindex`, supported version bitmask, and enabled version bitmask. `assoc` contains `dev-id`, `version`, nested `rx-key`/`tx-key`, and `sock-fd`. Nested `keys` carries raw `key` and `spi`. `stats` contains device id plus kernel and device counters such as key rotations, stale events, authenticated packet/byte counts, auth failures, framing errors, miscellaneous Rx errors, and Tx errors.

Control flow: `dev-get` does lookup or dump under `psp-device-get-locked`/`psp-device-unlock`; device add/delete/change notifications publish to `mgmt`. `dev-set` is admin-only and changes enabled versions. `key-rotate` is admin-only and publishes `key-rotate-ntf` to `use`. `rx-assoc` allocates an Rx key/SPI pair and associates a socket; `tx-assoc` installs a caller-provided Tx key; both use `psp-assoc-device-get-locked`. `get-stats` reads per-device counters and supports dump.

State and persistence: kernel PSP devices persist while the netdevice/device exists. Enabled versions, key rotation state, associations, socket bindings, and statistics live in kernel memory and are guarded by the named pre/post lock hooks. The YAML is declarative and does not persist data.

Dependencies and integration: integrates with PSP kernel support, generic netlink code generation, socket file descriptor passing semantics, and two multicast groups (`mgmt` and `use`). Userspace managers must subscribe to notifications for hotplug and key rotation.

Risks: key material is transported as binary netlink payloads and must be length-checked according to `version`; stale sockets may lose Rx after full key rotation; admin-only operations must remain protected. Test signals include schema validation, min-check enforcement for ids, notification coverage, lock-hook generation, key rotation event delivery, and association tests with valid/invalid socket FDs.
