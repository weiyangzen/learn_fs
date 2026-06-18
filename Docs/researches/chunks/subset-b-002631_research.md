# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h lines 7474-7483

## Purpose

This chunk closes the generated GC 9.1 register-offset header with DIDT stall-event counter register offsets and the final include-guard `#endif`. The relevant macros expose indexed (`ix`) offsets for Dynamic Inductive Droop Throttling telemetry counters in the graphics core:

- `ixDIDT_SQ_STALL_EVENT_COUNTER` at `0x00a0`
- `ixDIDT_DB_STALL_EVENT_COUNTER` at `0x00a1`
- `ixDIDT_TD_STALL_EVENT_COUNTER` at `0x00a2`
- `ixDIDT_TCP_STALL_EVENT_COUNTER` at `0x00a3`
- `ixDIDT_DBR_STALL_EVENT_COUNTER` at `0x00a4`

Lines 7474-7475 also show the immediately preceding DBR EDC telemetry offsets, which confirms this chunk belongs to the DIDT register block rather than ordinary memory-mapped `mm` GC registers.

## Important APIs, Types, And Data

The chunk contains only preprocessor constants. There are no C functions, structs, enums, or runtime APIs. The important API surface is the macro naming contract consumed by AMDGPU/PowerPlay register-access helpers:

- `ixDIDT_*` names identify indirect DIDT register offsets.
- The adjacent `gc_9_1_sh_mask.h` definitions describe these counter registers as a single full-width field: `DIDT_*_STALL_EVENT_COUNTER__DIDT_STALL_EVENT_COUNTER__SHIFT` is `0x0`, and the mask is `0xFFFFFFFFL`.
- The same mask header defines clear bits in `DIDT_SQ_CTRL0`, `DIDT_DB_CTRL0`, `DIDT_TD_CTRL0`, `DIDT_TCP_CTRL0`, and `DIDT_DBR_CTRL0` via `DIDT_STALL_EVENT_COUNTER_CLEAR` at bit 26.

The five blocks represented are shader queue (`SQ`), depth block (`DB`), texture data (`TD`), texture cache pipe (`TCP`), and depth block rasterizer (`DBR`) DIDT domains.

## Control Flow

There is no executable control flow in this header fragment. At compile time, users include this generated header to bind symbolic register names to literal offsets. Runtime control flow is introduced only by callers that pass these macros to SOC15/register-indexed accessors or table-driven PowerPlay programming sequences.

The closest local integration pattern appears in `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.c`, where DIDT control-register masks are listed in tables used to clear stall-event counters. That file references the clear bits rather than these counter offsets directly, but it shows how the DIDT counter state is managed: control-register writes clear hardware counters; later reads of the counter offsets can report accumulated stall events.

## State And Persistence Behavior

The macros themselves are stateless and compile-time-only. The hardware registers they name are volatile 32-bit counters with default value `0x00000000` in related GC generation default headers. Counter state is owned by GPU hardware and persists only until reset, power-gating/reset sequences, or explicit clearing through the corresponding `DIDT_*_CTRL0__DIDT_STALL_EVENT_COUNTER_CLEAR` bit.

No software persistence, disk state, or memory-backed cache is implemented here. Any sampling layer must handle wraparound because the masks indicate 32-bit counters.

## Dependencies

This header depends on the generated ASIC register layout staying synchronized with the GC 9.1 hardware specification. Consumers depend on:

- `gc_9_1_offset.h` for offsets.
- `gc_9_1_sh_mask.h` for field masks and shifts.
- AMDGPU SOC15/register helper macros that know how to address GC blocks and indexed register spaces.
- PowerPlay/DPM code that enables DIDT and clears or samples stall counters during power tuning.

The offsets match nearby GC 9.x headers such as `gc_9_0_offset.h`, `gc_9_2_1_offset.h`, and `gc_9_4_2_offset.h`, where these counters occupy `0x00a0` through `0x00a4`. GC 10.x moves comparable counters to `0x00c0` and later, so callers must include the generation-appropriate offset header.

## Integration Points

The immediate integration point is the AMDGPU generated ASIC register include tree under `drivers/gpu/drm/amd/include/asic_reg/gc/`. Higher-level users include this header through GC 9.1-specific register definitions and use the symbolic macros to avoid hard-coded offsets.

Potential runtime users include:

- PowerTune/DIDT setup and diagnostics code that clears or samples stall counters.
- Debug or telemetry paths that read DIDT counters for SQ, DB, TD, TCP, and DBR throttling behavior.
- ASIC-specific initialization tables that compare GC 9.1 register definitions with masks/defaults from sibling generated headers.

## Risks

- Incorrect offsets would silently read or write the wrong indirect DIDT register and could corrupt power-management behavior or produce misleading telemetry.
- Cross-generation reuse is risky: GC 9.x and GC 10.x use different DIDT counter offsets.
- Counter reads need wraparound-aware handling because each field is a full 32-bit hardware counter.
- Clearing counters through the related `CTRL0` clear bits is a destructive operation for telemetry consumers; sampling code should avoid racing with power-management code that resets the same counters.
- Since this file is generated-style register metadata, manual edits can diverge from AMD's ASIC register source and should be treated cautiously.

## Test Signals

Useful validation signals are mostly build-time and hardware/runtime oriented:

- Compile coverage for GC 9.1 AMDGPU code that includes `gc_9_1_offset.h`.
- Static checks that each `ixDIDT_*_STALL_EVENT_COUNTER` offset has a matching `gc_9_1_sh_mask.h` field mask and clear bit in the matching `DIDT_*_CTRL0` register.
- Runtime register-read smoke tests on supported GC 9.1 hardware showing DIDT stall counters read as 32-bit values and reset to zero after the corresponding clear bit is exercised.
- Power-management regression tests that enable DIDT/PowerTune paths without invalid register-access errors.
