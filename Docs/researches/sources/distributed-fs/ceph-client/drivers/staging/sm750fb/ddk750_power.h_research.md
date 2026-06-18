# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_power.h

Purpose: declares SM750 power-management types, DAC macro, and gate/power function prototypes.

Important APIs/types/functions: `enum dpms` defines CRT DPMS on/standby/suspend/off values. `set_DAC(off)` read-modify-writes `MISC_CTRL_DAC_POWER_OFF`. Prototypes expose DPMS, power mode, current gate, and engine gate helpers.

Control flow: the only inline behavior is `set_DAC(off)`, which directly updates the DAC power-off bit in `MISC_CTRL`; other behavior is implemented in `ddk750_power.c`.

State and persistence: no software state. Macro/function calls persist changes in hardware registers.

Dependencies and integration: relies on `poke32()`, `peek32()`, `MISC_CTRL`, and `MISC_CTRL_DAC_POWER_OFF` definitions from included chip/register headers through users. Used by display routing and hardware init.

Risks: `set_DAC` is a multi-statement macro without `do { } while (0)`, so it is unsafe in conditional contexts without braces. It performs direct read-modify-write with no locking.

Test signals: compile macro call sites, verify DAC bit behavior, and cover all DPMS enum values through `ddk750_set_dpms()`.
