<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_wa_oob.rules -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_wa_oob.rules

## Purpose
`xe_device_wa_oob.rules` is a data input file for generated out-of-band Xe device workarounds. Each rule maps a workaround identifier to platform, subplatform, display, or stepping predicates consumed by the workaround code generator.

## Important APIs, types, and functions
The file is not C code. Entries include `22010954014 PLATFORM(DG2)`, `15015404425 PLATFORM(LUNARLAKE) PLATFORM(PANTHERLAKE)`, `22019338487_display PLATFORM(LUNARLAKE)`, `14022085890 SUBPLATFORM(BATTLEMAGE, G21)`, and `14026539277 PLATFORM(NOVALAKE_P), PLATFORM_STEP(A0, B0)`. Continuation lines extend the previous rule, which is part of the parser contract in `xe_gen_wa_oob.c`.

## Control flow and integration points
Build tooling reads this file and emits generated C/header tables such as `generated/xe_wa_oob.h`. Driver code later queries the generated identifiers through `XE_DEVICE_WA()` or related helpers when deciding platform-specific behavior.

## State and persistence behavior
The rules persist as source data only. At build time they become enum identifiers and rule arrays; at runtime active workaround state is tracked under `xe->wa_active.oob`.

## Dependencies, risks, and test signals
Dependencies are the rule parser syntax, platform/subplatform/step vocabulary, and generated workaround consumers. Risks include malformed continuation lines, predicates that are too broad or too narrow, identifier collisions, or deleting rules still used by runtime code. Test signals are successful code generation, generated enum/table diffs, platform matrix validation, and runtime workaround activation logs on DG2, Lunar Lake, Battlemage G21, Panther Lake, and Nova Lake P steppings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_wa_oob.rules -->
