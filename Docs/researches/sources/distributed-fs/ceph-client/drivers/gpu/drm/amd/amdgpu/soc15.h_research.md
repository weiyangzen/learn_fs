# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.h

## Purpose

`soc15.h` is the public AMDGPU SOC15 common header. It defines small register-description structures and macros used by SOC15-era C files to express register offsets, golden-register programming, whitelisted register reads, and RAS error counter extraction. It also declares exported common IP blocks, register-base initialization entry points, SOC-specific doorbell initialization helpers, virtual operation setup, and Aqua Vanjaram configuration/state helpers.

## Important APIs, Types, And Functions

`struct soc15_reg_golden` carries a hardware IP, instance, segment, register offset, AND mask, and OR mask for golden-register programming. `struct soc15_allowed_register_entry` describes registers that may be exposed through debug/user read paths and includes a `grbm_indexed` flag for SE/SH-indexed reads. `struct soc15_ras_field_entry` describes RAS correctable/uncorrectable counter fields. Macros such as `SOC15_REG_ENTRY`, `SOC15_REG_GOLDEN_VALUE`, `SOC15_REG_FIELD`, and `SOC15_REG_ENTRY_OFFSET` standardize offset construction from generated register headers and `adev->reg_offset`.

## Control Flow

The header has no runtime control flow. It shapes call sites in files such as `soc15.c` and per-IP golden-register code: callers build static arrays of these structures, then pass them to routines like `soc15_program_register_sequence()` or compare requested register offsets against allow lists.

## State And Persistence Behavior

The structures are usually static metadata, but their offsets are interpreted against runtime `adev->reg_offset` tables initialized by `vega10_reg_base_init()`, `vega20_reg_base_init()`, `arct_reg_base_init()`, `aldebaran_reg_base_init()`, or Aqua Vanjaram setup. Incorrect metadata persists as hardware programming mistakes because it directly drives MMIO writes.

## Dependencies, Risks, And Test Signals

The header depends on NBIO variant declarations and `amdgpu_reg_state.h`. Its macros assume an in-scope `adev` variable, so misuse outside normal AMDGPU helper style is fragile. Risks are off-by-instance/segment errors, stale generated register names, and exposing the wrong register through an allow list. Compile coverage across SOC15 ASICs, golden-register table execution, RAS field parsing, and debug register read tests are the main signals.
