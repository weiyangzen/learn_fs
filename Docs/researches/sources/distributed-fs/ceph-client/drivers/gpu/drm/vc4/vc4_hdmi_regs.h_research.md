# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi_regs.h

## Purpose

`vc4_hdmi_regs.h` provides the logical register map and inline MMIO accessors for the VC4/VC5/VC6 HDMI driver. It abstracts hardware-generation register offsets behind `enum vc4_hdmi_field` values so the main driver and PHY code can use logical register IDs while the selected `vc4_hdmi_variant` supplies the correct base block and offset table.

## Important APIs, Types, and Functions

- `enum vc4_hdmi_regs` identifies register base regions: invalid, VC4 HDMI core, VC4 HD block, and VC5-style CEC/CSC/DVP/PHY/RAM/RM blocks.
- `enum vc4_hdmi_field` enumerates all logical HDMI registers used by the driver: audio packet/MAI registers, CEC control/data/interrupt registers, packet RAM, scheduler/timing, FIFO/video control, CSC, hotplug, scrambler, DVP/vector interface, PHY/PLL/RM registers, and format detection registers.
- `struct vc4_hdmi_register` maps a logical field to a base region and offset.
- `_VC4_REG()` and region macros construct register-table entries.
- Static register tables `vc4_hdmi_fields[]`, `vc5_hdmi_hdmi0_fields[]`, `vc5_hdmi_hdmi1_fields[]`, `vc6_hdmi_hdmi0_fields[]`, and `vc6_hdmi_hdmi1_fields[]` encode per-generation/per-port offsets.
- `__vc4_hdmi_get_field_base()` selects the MMIO base pointer from `struct vc4_hdmi`.
- `vc4_hdmi_read()` and `vc4_hdmi_write()` implement checked MMIO access. `HDMI_READ()` and `HDMI_WRITE()` are local convenience macros expecting a `vc4_hdmi` variable in scope.

## Control Flow

Driver code calls `HDMI_READ(field)` or `HDMI_WRITE(field, value)`. The inline accessor validates that runtime PM is not suspended, intentionally fails the current KUnit test if MMIO is attempted, checks the field index against `variant->num_registers`, resolves the `struct vc4_hdmi_register`, maps the base enum to an MMIO pointer, warns on invalid/unknown IDs, and performs `readl()` or `writel()`. Writes also assert `hw_lock` is held.

Resource init in `vc4_hdmi.c` builds debugfs regsets by iterating the same variant register table and filtering entries by base region, so this header is also the source of debugfs register visibility.

## State and Persistence

The header contains static constant register tables only. Live state is in `struct vc4_hdmi`: variant pointer, MMIO bases, platform device for PM status, and hardware lock. No persistent state exists; MMIO writes affect hardware registers until reset/power changes.

## Dependencies and Integration Points

The file includes runtime PM, `vc4_hdmi.h`, and relies on local bitfield helpers and the selected variant records in `vc4_hdmi.c`. It is used by both the HDMI control path and PHY path. Debugfs register dump construction also depends on table names and offsets remaining accurate.

## Risks and Edge Cases

- `enum vc4_hdmi_field` indexes directly into variant arrays; tables must include entries at the correct enum indexes or accesses will resolve to missing/incorrect registers.
- Some logical fields move between base regions by generation; missing MMIO base mapping causes runtime warnings and no-op reads/writes.
- Writes require `hw_lock`; adding write call sites without the lock trips lockdep and risks concurrent register modification.
- Runtime PM warnings catch suspended access but cannot make the access safe; callers must still hold PM references.
- KUnit tests intentionally fail on direct HDMI MMIO, so new tests need mocks or should validate higher-level state without invoking accessors.

## Test Signals

Useful checks include build-time coverage of all variant tables, debugfs regset completeness for each region, lockdep for writes, runtime PM warning absence during hotplug/audio/CEC/modesets, and KUnit tests that verify code avoids direct MMIO in mock contexts. Hardware smoke tests should compare debugfs register dumps against expected offsets for HDMI0/HDMI1 on BCM2711 and BCM2712.
