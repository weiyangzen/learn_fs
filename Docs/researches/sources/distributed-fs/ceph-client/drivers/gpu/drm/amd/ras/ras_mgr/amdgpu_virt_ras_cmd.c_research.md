# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_virt_ras_cmd.c

## Purpose

`amdgpu_virt_ras_cmd.c` implements VF-side remote unified RAS command support. It marshals `ras_cmd_ctx` commands through firmware-reserved shared VRAM, provides local wrappers for CPER and ECC queries, handles auto-updated block ECC buffers, and tracks remote unified RAS capability.

## Important APIs, Types, And Functions

Public functions initialize/finalize VF command state, run hardware init/fini, handle commands, pre/post reset, set/query remote unified RAS support, check retired-address validity, and convert retired addresses. Static helpers locate shared command memory, send remote ioctl commands, fetch batch trace overviews/records, generate CPER records from remote traces, register auto-update buffers, and serve block ECC status from shared memory.

## Control Flow, State, And Persistence

Remote command flow locks `remote_access_lock`, resolves the appropriate shared buffer, clears it, copies a command header, calls `amdgpu_virt_send_remote_ras_cmd` with GPA and length, then copies output back if sizes permit. CPER snapshot refreshes batch-trace overview; CPER record generation pulls remote batch records and writes generated CPER data to a userspace pointer. Block ECC status initializes an auto-update command in shared memory on first use, then reads cached per-block counts. HW init obtains RAS capability and binds the block ECC shared buffer; HW fini clears it; pre-reset disables auto-update state.

## Dependencies And Integration Points

It depends on SR-IOV firmware-reserved telemetry memory, AMDGPU virtualization remote command helpers, rascore command ABI, ras_log_ring and CPER generation, manager context, and memory reservation metadata. It is selected by `amdgpu_ras_submit_cmd` on VFs.

## Risks And Test Signals

Risks include incorrect CPU-to-GPA translation, shared buffer size/align errors, stale auto-update data after reset, user-copy failures, batch cache desynchronization, and command result confusion between transport `ret` and `cmd_res`. Test signals include VF remote command round trips, CPER snapshot/record reads, block ECC auto-update, reset pre/post behavior, invalid shared-memory reservation handling, address validity/retired conversion, and concurrent command serialization.
