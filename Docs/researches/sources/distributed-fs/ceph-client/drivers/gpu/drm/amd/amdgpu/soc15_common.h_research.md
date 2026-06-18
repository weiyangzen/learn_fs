# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15_common.h

## Purpose

`soc15_common.h` centralizes SOC15-style MMIO, RLC-mediated register access, logical-to-physical IP instance mapping, wait helpers, extended SMN access, and MCA 64-bit register access macros. It is a low-level integration header used by many AMDGPU IP blocks to avoid open-coding register base arithmetic and SR-IOV/RLCG access rules.

## Important APIs, Types, And Functions

`GET_INST()` and `GET_MASK()` consult `adev->ip_map` when logical device instances differ from hardware instances. `SOC15_REG_OFFSET()` and related offset macros compute MMIO offsets from generated register base indices. `RREG32_SOC15*` and `WREG32_SOC15*` variants perform reads/writes through `__RREG32_SOC15_RLC__` and `__WREG32_SOC15_RLC__`, which route through SR-IOV RLCG access when available. RLC-specific macros include `WREG32_RLC`, `WREG32_RLC_EX`, `WREG32_SOC15_RLC_SHADOW`, and `WREG32_SOC15_RLC_SHADOW_EX`. `SOC15_WAIT_ON_RREG*` wraps polling, while `RREG32_SOC15_EXT()`, `WREG32_SOC15_EXT()`, `RREG64_MCA()`, and `WREG64_MCA()` target extended SMN/MCA spaces.

## Control Flow

Most logic is macro-expanded at call sites. In SR-IOV VF mode with RLCG support, reads and writes are redirected to `amdgpu_sriov_rreg()`/`amdgpu_sriov_wreg()` with access flags; otherwise they become direct `RREG32()`/`WREG32()` operations. Full-access RLC writes can use scratch registers and a spare interrupt, polling for completion with a fixed retry loop.

## State And Persistence Behavior

The macros mutate hardware registers and sometimes RLC scratch state. They rely on stable `adev->reg_offset`, IP mapping callbacks, SR-IOV state, and RLC capability flags. No independent state is defined by the header, but every write changes persistent device register state until reset or later programming.

## Dependencies, Risks, And Test Signals

The header assumes AMDGPU core register macros, `adev` scope, generated register base symbols, and SR-IOV/RLC helpers. Risks include evaluating macro arguments with side effects, using direct access where KIQ/RLC access is required, wrong instance mapping, and timeout paths in `WREG32_RLC_EX`. Test signals include PF and VF register programming, KIQ/no-KIQ paths, RLC shadowed GRBM writes, wait helper timeout behavior, extended SMN access on multi-die hardware, and MCA register reads.
