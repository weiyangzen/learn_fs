<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/sysctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/sysctrl.yaml

## Purpose
This schema covers multiple HiSilicon system controller variants used for slave-core startup, reboot, clocks, resets, and related SoC control functions.

## Important APIs, Types, And Functions
It validates two compatible styles: generic/Hi6220/Hi3519 controllers followed by `syscon`, and HiP01 as `hisilicon,hip01-sysctrl`, `hisilicon,sysctrl`. Important properties include `reg`, `smp-offset`, `resume-offset`, `reboot-offset`, `#clock-cells`, `#reset-cells`, address/size cells, `ranges`, and `clock@` child nodes for `hisilicon,hi3620-clock` or `hisilicon,hi3620-mmc-clock`.

## Control Flow
An `allOf` conditional requires `#clock-cells` when `compatible` contains `hisilicon,hi6220-sysctrl`. `patternProperties` validates `clock@` children, while `additionalProperties` allows other child objects for controller subfunctions.

## State And Persistence
The binding describes persistent sysctrl registers and child clock register windows. Runtime state lives in syscon, reboot, SMP, clock, and reset drivers that use the offsets and child nodes.

## Dependencies And Integration Points
It integrates with Linux syscon, clock providers, reset providers, SMP boot code, and reboot paths. It depends on type definitions for uint32 offsets and on standard bus child-node conventions.

## Risks
Offset mistakes can affect CPU bring-up, resume, or reboot. The Hi6220 conditional is a compatibility trap: missing `#clock-cells` breaks clock consumers even if basic syscon probing succeeds.

## Test Signals
`dt_binding_check` exercises conditionals and examples. `dtbs_check`, SMP boot, suspend/resume, reboot, and clock consumer probing are practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/hisilicon/controller/sysctrl.yaml -->
