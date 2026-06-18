# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_virt_ras_cmd.h

## Purpose

`amdgpu_virt_ras_cmd.h` declares VF-side remote unified RAS command state and operations.

## Important APIs, Types, And Functions

Types include `remote_batch_trace_mgr`, `amdgpu_virt_shared_mem`, `vram_blocks_ecc`, and `amdgpu_virt_ras_cmd`. They store cached batch trace state, shared-memory CPU/GPA/size triples, auto-updated block ECC state, remote support flag, and a remote access mutex. Public APIs cover SW/HW init/fini, command handling, reset hooks, remote support toggles, address validity, and retired-address conversion.

## Control Flow, State, And Persistence

The header defines the state used to serialize remote commands and cache remote RAS data across calls. Shared-memory data persists in reserved VRAM until reset, fini, or explicit clearing.

## Dependencies And Integration Points

It includes `ras.h` and depends on `struct amdgpu_device`, rascore command structures, log batch types, and SR-IOV telemetry layout from AMDGPU virtualization code.

## Risks And Test Signals

Risks include lifetime errors for `virt_ras_cmd`, mutex use before init, stale `remote_uniras_supported`, and shared-memory buffer misuse. Test signals include VF init/fini, reset clearing, concurrent remote command tests, and capability toggling.
