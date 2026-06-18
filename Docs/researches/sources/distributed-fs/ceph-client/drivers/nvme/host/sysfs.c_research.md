# sources/distributed-fs/ceph-client/drivers/nvme/host/sysfs.c

## Purpose

`sysfs.c` defines the NVMe core sysfs interface for controllers, namespaces, namespace heads, multipath attributes, optional authentication/TLS attributes, and subsystems. It exposes read-only identity and state attributes, writable control knobs for reset/rescan/delete and fabrics timeout settings, passthrough error logging toggles, DH-HMAC-CHAP secret updates, and TCP TLS key status where configured. It exports attribute groups used by transports such as PCIe and RDMA.

## Important APIs, types, and functions

- Controller control attributes: `reset_controller`, `rescan_controller`, and `delete_controller`.
- Controller identity/state attributes: `model`, `serial`, `firmware_rev`, `cntlid`, `transport`, `subsysnqn`, `address`, `state`, `numa_node`, `queue_count`, `sqsize`, `hostnqn`, `hostid`, `kato`, `cntrltype`, `dctype`, and `quirks`.
- Fabrics timeout attributes: `ctrl_loss_tmo`, `reconnect_delay`, and `fast_io_fail_tmo`.
- Namespace attributes: `wwid`, `uuid`, `nguid`, `eui`, `csi`, `nsid`, `metadata_bytes`, `nuse`, and `passthru_err_log_enabled`; multipath builds add ANA and queue-depth related attributes from other compilation units.
- `dev_to_ns_head` abstracts namespace-head versus per-path disk access.
- `ns_head_update_nuse`, `ns_update_nuse`, and `nuse_show` rate-limit Identify Namespace commands before exposing current namespace utilization.
- Attribute visibility callbacks are `nvme_ns_attrs_are_visible`, `nvme_dev_attrs_are_visible`, `nvme_tls_attrs_are_visible`, and multipath group visibility helpers.
- Authentication handlers are `nvme_ctrl_dhchap_secret_store` and `nvme_ctrl_dhchap_ctrl_secret_store` under `CONFIG_NVME_HOST_AUTH`.
- TCP TLS handlers are `tls_key_show`, `tls_configured_key_show`, `tls_configured_key_store`, `tls_keyring_show`, and `tls_mode_show` under `CONFIG_NVME_TCP_TLS`.
- Exported groups include `nvme_ns_attr_groups`, `nvme_dev_attrs_group`, `nvme_dev_attr_groups`, and `nvme_subsys_attrs_groups`.

## Control flow

Sysfs show/store callbacks start from a `struct device`, recover the relevant `nvme_ctrl`, `nvme_ns`, `nvme_ns_head`, or `nvme_subsystem`, and use `sysfs_emit` for output. Reset calls `nvme_reset_ctrl_sync`, rescan queues a namespace scan, and delete uses `device_remove_file_self` before invoking transport `delete_ctrl` through `nvme_delete_ctrl_sync`. The delete attribute is hidden unless the transport provides a delete operation.

Namespace identity output prefers globally stable identifiers. `wwid_show` emits UUID when present, then NGUID, then EUI64, and finally a legacy vendor/serial/model/nsid string with trailing blanks removed. `uuid_show` preserves backward compatibility by exposing NGUID as UUID if no UUID exists, with a one-time warning. Visibility hides UUID/NGUID/EUI attributes when the underlying identifier is absent.

`nuse_show` updates `head->nuse` through an Identify Namespace command unless rate-limited. For multipath namespace-head disks, it selects an active path under SRCU; for per-path namespaces it queries the concrete namespace controller. The value is then emitted from namespace-head state.

Controller fabrics timeout stores parse integer input and update `ctrl->opts` fields directly. Negative `ctrl_loss_tmo` or `fast_io_fail_tmo` maps to "off"; `ctrl_loss_tmo` converts seconds into `max_reconnects` using the current reconnect delay. These attributes are visible only when `ctrl->opts` exists.

Authentication store paths validate DHCHAP secret syntax, allocate a replacement string, stop current authentication, parse the new key, swap key pointers under `dhchap_auth_mutex`, free old key material, and queue re-authentication work. TLS configured-key store only accepts `0`, negotiates a new key for concat mode, waits for auth completion, and resets the controller so the TLS connection is recreated.

## State and persistence behavior

Most attributes expose live kernel state stored in `nvme_ctrl`, `nvmf_ctrl_options`, `nvme_ns_head`, and `nvme_subsystem`. Writable attributes mutate in-memory controller options and flags. Reset, rescan, delete, re-authentication, and TLS key regeneration trigger asynchronous or synchronous controller behavior beyond sysfs state.

`passthru_err_log_enabled` is a per-controller or per-namespace-head boolean. `ctrl_loss_tmo`, `reconnect_delay`, and `fast_io_fail_tmo` mutate fabrics option fields and affect later recovery behavior. DHCHAP secret updates replace dynamically allocated option strings and parsed key objects; old key objects are freed. TLS attributes expose kernel key serials and configured keyring descriptions without persisting secrets in this file.

`nuse` is cached on the namespace head and refreshed opportunistically with rate limiting. Subsystem identity strings and subtype are owned by the NVMe subsystem object, not by sysfs.

## Dependencies and integration points

The file depends on NVMe core types and helpers from `nvme.h`, fabrics options from `fabrics.h`, Linux sysfs/device/gendisk conventions, optional multipath symbols, optional `linux/nvme-auth.h` support, keyring objects for TLS, and core workqueues such as `nvme_wq`.

Transport drivers consume these groups through `nvme_ctrl_ops.dev_attr_groups` or by composing `nvme_dev_attrs_group` with transport-specific groups. Namespace block devices use `nvme_ns_attr_groups`, and subsystem devices use `nvme_subsys_attrs_groups`. The file also integrates with controller operations such as `get_address`, `delete_ctrl`, reset, scan, Identify Namespace, authentication negotiation, and controller reset.

## Risks and edge cases

- Store callbacks directly change recovery/authentication settings; invalid parsing or missing visibility checks can expose attributes for controllers that do not support them.
- DHCHAP stores echo configured secrets through read attributes. This matches the file behavior but is sensitive from an operational perspective.
- Updating DHCHAP keys requires careful ordering: stop auth, parse new key, swap under mutex, free old key, and queue re-authentication. Errors must leave the previous valid secret intact.
- `nuse_show` issues Identify commands from a read path and can fail with path errors; rate limiting prevents excessive admin commands but may expose stale usage.
- Multipath visibility must hide per-path-only attributes on namespace heads and hide namespace-head-only attributes on paths.
- TLS key regeneration resets the controller; failed negotiation or wait also triggers reset, so userspace writes can be disruptive.
- WWID fallback depends on trimmed serial/model bytes and namespace ID. Devices with bogus identifiers may still produce unstable legacy IDs.

## Test signals

Validate sysfs file presence and permissions for PCIe, RDMA, TCP, discovery, admin, multipath, and non-multipath controllers. Exercise reset, rescan, delete, timeout stores, passthrough logging toggles, namespace identifier visibility, `nuse` refresh and rate limiting, DHCHAP secret replacement and re-authentication, TLS concat key regeneration, TLS visibility gates, subsystem identity attributes, and transport-specific hiding of address/delete/host fields. Negative tests should cover malformed booleans, integers, DHCHAP prefixes, unsupported TLS writes, absent identifiers, and no-path multipath namespace-head reads.
