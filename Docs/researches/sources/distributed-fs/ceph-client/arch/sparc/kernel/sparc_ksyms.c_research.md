# sources/distributed-fs/ceph-client/arch/sparc/kernel/sparc_ksyms.c

Purpose: exposes the architecture symbol `saved_command_line` to loadable modules.

Important APIs/types/functions: the file only includes `linux/export.h` and uses `EXPORT_SYMBOL(saved_command_line)`.

Control flow: there is no runtime control flow. The export is consumed by module symbol resolution.

State and persistence: the exported state is the kernel boot command line already maintained elsewhere; this file does not mutate or persist it.

Dependencies and integration points: specifically documents the dependency from `drivers/sbus/char/openprom.c` and any other module requiring the saved boot command line.

Risks: removing or renaming the export can break out-of-tree or modular OpenPROM users. There is no functional logic to test beyond symbol availability.

Test signals: modular builds should link users of `saved_command_line`; `modpost` should not report unresolved symbols for OpenPROM-related modules.
