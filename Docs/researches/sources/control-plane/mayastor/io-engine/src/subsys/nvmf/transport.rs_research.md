# sources/control-plane/mayastor/io-engine/src/subsys/nvmf/transport.rs

Purpose: builds SPDK NVMe-oF transports and formats transport IDs/URIs for the target. It is the bridge from Mayastor configuration and environment IP selection to SPDK `spdk_nvme_transport_id` and `spdk_nvmf_transport_create` calls.

Important APIs/types/functions: `create_and_add_transports(add_rdma)` creates TCP transport from `Config::nvmf_tgt_conf.opts_tcp`, adds it to `NVMF_TGT`, then optionally creates/adds RDMA from `opts_rdma`. `TransportId` wraps `spdk_nvme_transport_id` with `Deref`, `DerefMut`, `Display`, `Debug`, `new`, and `as_ptr`. `get_ip_address` maps `MayastorEnvironment::get_nvmf_tgt_ip` into the local NVMf `Error`.

Control flow: TCP transport creation is mandatory; null creation maps to `Error::Transport`. Adding a transport uses an SPDK completion callback bridged through a futures oneshot channel. RDMA is optional: creation failure is logged and treated as success so the target can run TCP-only; add completion is awaited with `.ok()` and does not propagate a failed callback result. `TransportId::new` chooses TCP or RDMA constants, IPv4/IPv6 address family, fills SPDK fixed arrays via `copy_cstr_with_null`/`copy_str_with_null`, and asserts service-id length.

State and persistence: no durable state. Static lazy `CString`s provide stable C string storage for TCP/RDMA names. The generated transport ID includes the current configured target IP and port at construction time.

Dependencies and integration points: depends on SPDK NVMf/NVMe constants and functions, Mayastor `Config`, target thread-local `NVMF_TGT`, `MayastorEnvironment`, `SIpAddr`, and FFI callback helpers. `Display` output becomes the NVMf URI form used by share paths; RDMA displays as `nvmf+rdma+tcp://...` to signal dual support.

Risks and edge cases: RDMA add errors are ignored after channel await, so a transport-add failure can be hidden. `TransportId::new` unwraps IP resolution and asserts port string length. IPv6 scope IDs are explicitly not handled. The TCP add result is awaited but assigned to `_result` without `?`, so callback errno may not affect success; only transport creation failure is propagated.

Test signals: indirectly covered by NVMf share and connect tests, especially URI parsing/connection in `mount_fs.rs`, `ftl_mount_fs.rs`, and `block_device_nvmf.rs`.
