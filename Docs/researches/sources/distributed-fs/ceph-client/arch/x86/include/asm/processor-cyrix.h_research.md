# sources/distributed-fs/ceph-client/arch/x86/include/asm/processor-cyrix.h

Purpose: provides ordered inline accessors for NSC/Cyrix CPU indexed configuration registers using the legacy PC configuration port pair.

Important APIs, types, and functions: includes `pc-conf-reg.h` and defines `getCx86(u8 reg)` and `setCx86(u8 reg, u8 data)` as wrappers around `pc_conf_get()` and `pc_conf_set()`.

Control flow: `getCx86()` writes the index and reads data through `pc_conf_get()`. `setCx86()` writes the index and value through `pc_conf_set()`. The functions are inline rather than macros to preserve access ordering.

State and persistence: reads and writes CPU/chipset indexed registers. State persists in hardware until reset or later modification.

Dependencies and integration points: used by old Cyrix/NSC CPU identification and setup code, relying on `pc_conf_lock` discipline from callers where concurrent access matters.

Risks: ordering through ports `0x22/0x23` is mandatory. Wrong registers can change CPU/chipset behavior on legacy hardware.

Test signals: legacy Cyrix CPU detection/setup builds, ordered I/O tracing, register readback after writes, and regression tests for callers that serialize indexed access.
