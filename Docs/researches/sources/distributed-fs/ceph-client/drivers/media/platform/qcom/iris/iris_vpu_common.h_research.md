# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_common.h

## Purpose
`iris_vpu_common.h` is the public interface for Iris VPU hardware operations. It declares the per-generation `vpu_ops` tables and the shared controller, firmware, interrupt, power, and frequency functions implemented by `iris_vpu_common.c`.

## Important APIs And Types
- `struct vpu_ops` defines platform operation slots: `power_off_hw`, `power_on_hw`, `power_off_controller`, `power_on_controller`, optional `program_bootup_registers`, `calc_freq`, and `set_hwmode`.
- Extern operation tables: `iris_vpu2_ops`, `iris_vpu3_ops`, `iris_vpu33_ops`, `iris_vpu35_ops`, and `iris_vpu4x_ops`.
- Public functions cover firmware boot, interrupt raise/clear, watchdog check, PC preparation, power on/off split by controller/hardware, hardware mode switching, VPU35/VPU4x controller functions, boot-register programming, and frequency calculation.

## Control Flow And Integration
Platform data embeds a `const struct vpu_ops *`; higher-level Iris core and PM code call through this table to execute generation-specific sequences while sharing common helpers. Optional hooks such as `program_bootup_registers` allow VPU35/VPU4x to write extra registers during queue/SFR setup.

## State And Persistence
No state is stored in the header. It forward-declares `struct iris_core`; several declarations also use `struct iris_inst` through the `calc_freq` callback and exported frequency helper, relying on other includes to provide that type in compilation units.

## Dependencies
Requires kernel integer types and `struct iris_core`/`struct iris_inst` definitions in users. It is tightly coupled to Iris platform data and clock/power/reset helpers.

## Risks
- Any mismatch between an operation table and hardware generation can produce incorrect power sequencing.
- Function declarations expose split controller/hardware stages; callers must maintain the correct ordering and unwind paths.
- Header forward declarations are minimal; include-order mistakes can surface where `struct iris_inst` is not visible.

## Test Signals
Build coverage validates operation table signatures. Runtime validation comes from platform probe, firmware boot, suspend/resume, power collapse, watchdog recovery, and frequency scaling on all declared VPU generations.
