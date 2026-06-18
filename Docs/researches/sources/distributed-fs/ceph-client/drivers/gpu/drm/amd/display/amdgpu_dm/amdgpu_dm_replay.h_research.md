# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_replay.h

### Purpose
`amdgpu_dm_replay.h` declares the AMDGPU DM Panel Replay interface and public enable-option bit definitions used to configure replay behavior.

### Important APIs, Types, And Functions
It defines `enum replay_enable_option` bits for static screen, MPO video, full-screen video, general UI, and their coasting variants. It declares link support, capability setup, link setup, enable, disable, and global disable helpers.

### Control Flow
The header has no runtime control flow. It provides compile-time contracts for embedded-panel replay setup and runtime power-management callers.

### State, Persistence, And Dependencies
No state is stored here. It includes `amdgpu.h` and references DC link/stream and AMDGPU DM connector/display-manager types used by the implementation.

### Integration Points
Used by display-manager link setup, connector capability paths, and runtime commit code that enables or disables replay around updates.

### Risks
Enable-option bit changes affect firmware-facing replay config semantics. Declaration drift would break callers in DM and link setup code.

### Test Signals
Build replay-capable configurations and run panel replay capability, enable/disable, and global disable paths on eDP hardware.
