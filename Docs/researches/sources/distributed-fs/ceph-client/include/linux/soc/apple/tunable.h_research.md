# sources/distributed-fs/ceph-client/include/linux/soc/apple/tunable.h

Purpose: This header describes Apple tunable register programming parsed from firmware/device-tree data and applied to MMIO blocks.

Important APIs/types/functions: `struct apple_tunable` holds parsed register/value/mask style data for a tunable sequence. `devm_apple_tunable_parse` parses a named property or node for a device and returns managed tunable data. `apple_tunable_apply(void __iomem *regs, struct apple_tunable *tunable)` applies the sequence to a mapped register block.

Control flow: Platform drivers parse tunables during probe, map their hardware registers, then apply the tunable at the appropriate initialization or power-up point.

State and persistence: Parsed tunable data is managed with the device lifetime. Applied values persist in hardware registers until reset, power loss, or later writes.

Dependencies and integration: Uses `struct device` and MMIO annotations. It integrates with Apple SoC drivers that need firmware-provided register tweaks without hard-coding every variant.

Risks and test signals: Wrong property parsing, missing masks, or applying tunables before clocks/resets are ready can corrupt hardware setup. Test absent properties, malformed entries, probe deferral, power-cycle reapplication, and readback of expected register fields.
