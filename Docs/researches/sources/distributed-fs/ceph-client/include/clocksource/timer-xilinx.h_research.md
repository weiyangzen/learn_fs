# sources/distributed-fs/ceph-client/include/clocksource/timer-xilinx.h

Purpose: Xilinx AXI timer register definitions and shared private helper interface.

Important APIs/types/functions: register offsets `TCSR*`, `TLR*`, `TCR*`; control bits `TCSR_MDT` through `TCSR_CASC`; `struct xilinx_timer_priv`; `xilinx_timer_tlr_cycles`; and `xilinx_timer_get_period`.

Control flow: drivers program counter control/status registers, convert desired periods to load-register values, and convert current load/control values back to nanosecond periods.

State and persistence: `xilinx_timer_priv` carries regmap, parent clock, and counter maximum. Hardware registers hold active timer state.

Dependencies and integration points: integrates with regmap, clk, device-tree clocksource/clockevent/PWM users.

Risks: callers must ensure cycle counts are representable as TLR values. Up/down and cascade bits affect period math; using wrong `tcsr` flags gives wrong timing.

Test signals: Xilinx timer probe tests, period conversion unit tests, clockevent tick validation, and PWM/clocksource coexistence.
