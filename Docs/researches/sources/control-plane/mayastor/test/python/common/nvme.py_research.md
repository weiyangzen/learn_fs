# sources/control-plane/mayastor/test/python/common/nvme.py

## Purpose
Shared NVMe CLI helpers for kernel and remote initiator tests. It connects, discovers, disconnects, identifies, and inspects NVMe/TCP devices and controllers.

## Important APIs, Types, And Functions
Exports `nvme_hostids`, remote helpers `nvme_remote_connect_all`, `nvme_remote_connect`, `nvme_remote_disconnect`, `nvme_remote_discover`, local helpers `nvme_connect`, `nvme_id_ctrl`, `nvme_find_ctrl`, `nvme_resv_report`, `nvme_discover`, `nvme_disconnect`, `nvme_disconnect_controller`, `nvme_disconnect_all`, `nvme_list_subsystems`, `identify_namespace`, and `nvme_delete_controller`.

## Control Flow
URI helpers parse NVMf URLs into host, port, and NQN, run `nix-sudo nvme` commands, parse JSON outputs, assert a single matching subsystem/controller where required, and return device paths or metadata. Forced controller deletion writes to `/sys/class/nvme/<ctrl>/delete_controller`.

## State And Persistence
State is in kernel NVMe subsystems/controllers and optional host ID/NQN environment variables. The module does not cache state.

## Dependencies And Integration Points
Depends on `nvme-cli`, `nix-sudo`, `json`, `/sys`, async SSH via `run_cmd_async_at`, and Mayastor NVMf URI conventions. Used by ANA, nexus, multipath, fault, and Kubernetes-adjacent tests.

## Risks
Helpers assume exactly one matching connection in several paths and can disrupt host NVMe state through `disconnect-all` or forced controller deletion. The remote discover helper has a likely bug from awaiting `.stdout` on the coroutine result expression incorrectly.

## Test Signals
Successful discovery/connect/list/reservation-report calls are strong datapath and multipath signals for Mayastor NVMf exports.
