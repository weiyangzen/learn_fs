# sources/distributed-fs/ceph-client/drivers/infiniband/core/security.c

## Purpose
`security.c` enforces LSM-backed InfiniBand security policy for QP PKey access and MAD/SMP management access. It tracks QPs by port/PKey index so cache changes can move unauthorized QPs to error, manages security blobs for QPs and MAD agents, and handles shared QP security relationships.

## Important APIs, types, and functions
- QP security lifecycle: `ib_create_qp_security()`, `ib_destroy_qp_security_begin()`, `ib_destroy_qp_security_abort()`, `ib_destroy_qp_security_end()`.
- Shared QP APIs: `ib_open_shared_qp_security()` and `ib_close_shared_qp_security()`.
- Enforcement/update APIs: `ib_security_modify_qp()`, `ib_security_cache_change()`, `ib_security_release_port_pkey_list()`.
- MAD security APIs: `ib_mad_agent_security_setup()`, `ib_mad_agent_security_cleanup()`, `ib_mad_agent_security_change()`, and `ib_mad_enforce_security()`.
- Internal helpers include `check_qp_port_pkey_settings()`, `enforce_qp_pkey_security()`, `qp_to_error()`, and port/PKey list insertion/removal.

## Control flow and behavior
For IB devices, QP creation allocates an LSM security blob and initializes a mutex, shared-QP list, error completion, and counters. QP modification that changes primary or alternate port/PKey builds a proposed `ib_ports_pkeys`, inserts it into per-port/PKey tracking lists before policy checking to avoid cache-update races, validates the real QP and all shared QPs through `security_ib_pkey_access()`, and only then calls the driver `modify_qp`. On success it replaces old tracked settings; on failure it removes the proposed entries.

When the cached PKey or subnet prefix changes, `ib_security_cache_change()` walks affected PKey lists. Any QP whose current security blob no longer has access is queued to a local error list, then under its security mutex moved to `IB_QPS_ERR` and notified through QP fatal events. Destroy begin removes tracked PKeys and records how many concurrent error-list completions are pending; abort restores tracking and revalidates; end waits for pending error handling and frees security state.

MAD setup allocates security blobs. SMI agents additionally require `security_ib_endport_manage_subnet()`, are tracked in a global list, and have `smp_allowed` refreshed by `ib_mad_agent_security_change()`. MAD sends enforce either SMP management permission or PKey permission based on QP type.

## State, persistence, and dependencies
Per-device port data owns PKey index lists protected by spinlocks. Each `ib_qp_security` stores the QP pointer, device, LSM blob, tracked port/PKey settings, shared QP list, mutex, destroying flag, error-list counters, and completion. Global `mad_agent_list` tracks SMI agents under `mad_agent_list_lock`.

## Integration points
This file integrates with Linux security hooks (`security_ib_alloc_security`, `security_ib_free_security`, `security_ib_pkey_access`, `security_ib_endport_manage_subnet`), RDMA cache helpers for PKey/subnet prefix lookup, QP driver modify callbacks, MAD core private structures, and IB event callbacks.

## Risks and test signals
Risks include races between QP modify/destroy and PKey cache updates, list corruption from shared QP handling, missing security context on IB QPs, failure to notify shared QPs on fatal policy changes, SMP permission staleness, and deadlocks between spinlocks and QP security mutexes. Test signals include SELinux/LSM policy allow/deny cases, QP modify to denied PKey, PKey table changes after QP creation, destroy abort during cache-change enforcement, SMI agent permission changes, and non-IB device bypass behavior.
