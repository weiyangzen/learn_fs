<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.h

## Purpose

`arcturus_ppt.h` declares the Arcturus PPT installer and local DPM table structures used by the Arcturus SMU11 implementation. It gives the `.c` file and any selector code the function needed to attach Arcturus-specific `pptable_funcs` to an SMU context.

## Important APIs, Types, and Functions

The header defines UMD pstate indexes for GFXCLK, SOCCLK, and MCLK, `MAX_DPM_NUMBER`, `MAX_PCIE_CONF`, `arcturus_dpm_level`, `arcturus_dpm_state`, `arcturus_single_dpm_table`, `arcturus_pcie_table`, `arcturus_dpm_table`, and `extern void arcturus_set_ppt_funcs(struct smu_context *smu)`.

## Control Flow

There is no code flow in the header. At runtime, platform dispatch calls `arcturus_set_ppt_funcs`, implemented in `arcturus_ppt.c`, to install Arcturus maps and hooks. The DPM structs describe per-clock DPM levels and min/max state used by platform logic.

## State and Persistence Behavior

The header defines shapes for state but stores none itself. Arcturus DPM state persists in the SMU context after allocation and population from firmware/PPTable data.

## Dependencies

It depends on `bool`, fixed-width integer types, and a visible declaration of `struct smu_context` from surrounding includes. The DPM maxima must align with firmware/table expectations.

## Integration Points

Compiled users include Arcturus platform setup and common SMU selector code. The constants are used to choose standard/peak UMD pstate levels and allocate bounded DPM arrays.

## Risks and Edge Cases

The local `MAX_PCIE_CONF` name overlaps with generation headers; include order must avoid conflicting definitions. Fixed DPM array sizes require bounds checks before indexing. UMD pstate indexes are meaningful only when the firmware reports enough levels.

## Test Signals

Build coverage, Arcturus function-table installation, DPM table population with level counts at or below `MAX_DPM_NUMBER`, and UMD pstate reporting are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.h -->
