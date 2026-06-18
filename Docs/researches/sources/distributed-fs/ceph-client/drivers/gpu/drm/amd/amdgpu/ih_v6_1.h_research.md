# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_1.h

## Purpose
`ih_v6_1.h` declares the amdgpu IH v6.1 IP block object for consumers that build IP version tables.

## Important APIs, Types, And Functions
The only API is `extern const struct amdgpu_ip_block_version ih_v6_1_ip_block;`.

## Control Flow
There is no runtime control flow. Inclusion enables static registration of the implementation in `ih_v6_1.c`.

## State And Persistence
The header owns no mutable state. It exposes a const IP block descriptor.

## Dependencies And Integration Points
It depends on include sites knowing `struct amdgpu_ip_block_version` and integrates with the amdgpu IP discovery/initialization framework.

## Risks
Declaration/definition mismatch would surface as compile or link failures. The header does not itself reveal the implementation's version metadata, so version-label mistakes must be caught in C-file review or runtime selection tests.

## Test Signals
Build coverage and device-selection coverage for `ih_v6_1_ip_block` are the key signals.
