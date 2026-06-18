# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-madera.h

Purpose: Shared declarations for the Madera pinctrl core and chip-specific group tables.

Important APIs/types/functions: `struct madera_pin_groups` describes an alternate function group; `struct madera_pin_chip` describes chip GPIO count and group table; `struct madera_pin_private` is the runtime core state. Extern declarations expose CS47L15/35/85/90/92 chip tables.

Control flow: chip-specific C files instantiate `madera_pin_chip`; the common core selects one by MFD type and stores it in `madera_pin_private`.

State and persistence: no state here; runtime state is allocated in the core and hardware state is in codec registers.

Dependencies/integration: used by all Cirrus Madera pinctrl sources and depends on the Madera MFD type declarations being visible in including C files.

Risks: extern declarations and Makefile object inclusion must remain aligned. Adding a new codec requires updating this header, Kconfig, Makefile, and core type switch together.

Test signals: compile all chip selector combinations and verify no unresolved externs or missing switch cases.
