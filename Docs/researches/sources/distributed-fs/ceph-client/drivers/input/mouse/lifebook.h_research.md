# sources/distributed-fs/ceph-client/drivers/input/mouse/lifebook.h

`lifebook.h` declares `lifebook_detect()`, `lifebook_init()`, and `lifebook_module_init()` for the psmouse core. When `CONFIG_MOUSE_PS2_LIFEBOOK` is disabled, `lifebook_module_init()` is a no-op inline so `psmouse_init()` can call it unconditionally.

The header defines no state. Its main integration point is startup ordering: DMI state is initialized before the serio psmouse driver is registered. Risks are Kconfig/table mismatches causing unresolved symbols or missing DMI initialization.

Test signals are builds with Lifebook support enabled and disabled, and confirmation that DMI matching runs only in supported builds.
