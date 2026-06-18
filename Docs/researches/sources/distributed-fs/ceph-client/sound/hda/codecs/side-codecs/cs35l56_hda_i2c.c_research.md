# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l56_hda_i2c.c

## Purpose
This file is the I2C transport binding for CS35L54/56/57 HDA smart amplifiers. It allocates the shared HDA object, creates the I2C regmap, passes the I2C address and chip HID to common probe, then requests the device IRQ.

## Important APIs, types, and functions
`cs35l56_hda_i2c_probe()` allocates `struct cs35l56_hda`, sets `base.dev`, optionally enables hibernate capability at compile time, initializes `base.regmap` with `cs35l56_regmap_i2c`, calls `cs35l56_hda_common_probe(cs35l56, id->driver_data, clt->addr)`, and then calls `cs35l56_irq_request()`. The id table maps `cs35l54-hda`, `cs35l56-hda`, and `cs35l57-hda` to chip ids `0x3554`, `0x3556`, and `0x3557`. The ACPI table matches `CSC3554`, `CSC3556`, and `CSC3557`.

## Control flow
Probe is linear: allocate, initialize regmap, common probe, IRQ request. If IRQ request fails after common probe succeeded, it calls `cs35l56_hda_remove()` to unwind common state. Remove forwards to common remove. The driver uses `cs35l56_hda_pm_ops` for PM.

## State and persistence
Local state is only the devm allocation and regmap setup. The common object persists as device drvdata after common probe. The I2C address is used as the id for ACPI amp-index matching.

## Dependencies and integration points
It depends on Linux I2C/regmap/module infrastructure and the shared CS35L56 HDA/common Cirrus namespaces. Integration with IRQ handling is via `cs35l56_irq_request()` from the shared CS35L56 support code.

## Risks and edge cases
Failure after common probe must unwind both component and runtime-PM state; this file explicitly does that for IRQ failures. `i2c_client_get_device_id()` must produce a valid id because driver data selects chip type. Address aliases that are not real amps are rejected later by common ACPI parsing.

## Test signals
Probe each supported ACPI id, validate regmap creation, verify I2C address to `cirrus,dev-index` mapping, test IRQ request success/failure unwind, suspend/resume through shared PM ops, and module remove with no leaked component registration.
