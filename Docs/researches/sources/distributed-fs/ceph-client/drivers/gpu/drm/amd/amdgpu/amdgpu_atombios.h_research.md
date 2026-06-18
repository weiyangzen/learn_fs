# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atombios.h

## Purpose
`amdgpu_atombios.h` declares the legacy ATOMBIOS data structures and helper APIs consumed by AMDGPU display, clock, power, memory, and initialization code. It is the private interface for code that needs parsed legacy VBIOS information or ATOM command execution results.

## Important APIs, types, and functions
Key types include `struct atom_clock_dividers`, `struct atom_mpll_param`, `struct atom_memory_info`, `struct atom_memory_clock_range_table`, `struct atom_mc_reg_table`, and voltage-table structures. Constants define memory type encodings, AC timing limits, MC register array limits, and voltage entry limits. Prototypes expose GPIO/I2C lookup/init, connector object parsing, clock/gfx/VRAM info, spread-spectrum info, clock dividers, SI-only memory PLL/timing/voltage helpers, GPU virtualization table detection, BIOS scratch manipulation, endian-safe ATOM copy, data-table lookup, lifecycle init/fini, and sysfs init.

## Control flow
The header has no executable flow. It defines the call surface implemented by `amdgpu_atombios.c`: callers initialize the ATOM context, query tables or execute commands through these helpers, then tear the context down at device shutdown.

## State and persistence behavior
The declared structures are transient containers for values parsed from VBIOS tables or returned by ATOM command tables. They do not own persistent storage. Functions declared here update `struct amdgpu_device` runtime fields, hardware scratch registers, and caller-provided output buffers.

## Dependencies and integration points
The header assumes AMDGPU core types such as `struct amdgpu_device`, GPIO/I2C records, `struct amdgpu_atom_ss`, and UMA/clock-related structures are visible to includers. `CONFIG_DRM_AMDGPU_SI` gates older Southern Islands helpers. It integrates legacy ATOMBIOS parsing with display, power management, memory controller setup, and sysfs.

## Risks and edge cases
Many structures contain endian-sensitive bitfields that must match ATOM firmware layouts. Constants such as `VBIOS_MC_REGISTER_ARRAY_SIZE`, `VBIOS_MAX_AC_TIMING_ENTRIES`, and `MAX_VOLTAGE_ENTRIES` must stay aligned with implementation bounds checks. The header repeats the `amdgpu_atombios_get_clock_dividers()` prototype, which is harmless but a maintenance smell.

## Test signals
Build coverage with and without `CONFIG_DRM_AMDGPU_SI`, big-endian compile coverage for bitfields and `copy_swap()`, and runtime table parsing on legacy VBIOS revisions are the main validation signals.
