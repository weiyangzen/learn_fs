# sources/distributed-fs/ceph-client/drivers/usb/typec/altmodes/Makefile

## Purpose

`drivers/usb/typec/altmodes/Makefile` maps alternate-mode Kconfig symbols to the DisplayPort, NVIDIA, and Thunderbolt driver objects.

## Important APIs, Types, and Functions

`CONFIG_TYPEC_DP_ALTMODE` builds `typec_displayport.o` from `displayport.o`; `CONFIG_TYPEC_NVIDIA_ALTMODE` builds `typec_nvidia.o` from `nvidia.o`; `CONFIG_TYPEC_TBT_ALTMODE` builds `typec_thunderbolt.o` from `thunderbolt.o`.

## Control Flow

Kbuild evaluates `obj-$()` expressions and composite object definitions. Selected drivers are built as modules or built-ins according to their tristate values.

## State and Persistence Behavior

There is no runtime state. The file controls build artifacts only.

## Dependencies and Integration Points

It must match `altmodes/Kconfig` symbols and the module driver names registered in the corresponding C files. NVIDIA relies on the DisplayPort object exporting probe/remove helpers when built together according to Kconfig dependency rules.

## Risks and Edge Cases

Stale composite names break module naming or linking. If a driver gains multiple source files, this Makefile must add them to the right composite object rather than as separate modules.

## Test Signals

Run allmodconfig and per-symbol builds to verify `typec_displayport`, `typec_nvidia`, and `typec_thunderbolt` objects link with expected module names.
