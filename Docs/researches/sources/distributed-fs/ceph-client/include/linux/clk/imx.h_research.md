# sources/distributed-fs/ceph-client/include/linux/clk/imx.h

Purpose: This header exposes an i.MX6SL clock-control hook for wait-mode clock handling.

Important APIs/types/functions: The API is `imx6sl_set_wait_clk(bool enter)`, declared after including `<linux/types.h>`.

Control flow: i.MX platform PM code calls this hook when entering or leaving wait mode; the implementation adjusts the SoC wait clock selection or gating.

State and persistence behavior: State lives in SoC clock registers. The boolean indicates transition direction; the header stores no state.

Dependencies and integration points: It integrates i.MX clock code with low-power state entry/exit code and architecture-specific PM flows.

Risks: Calling it for the wrong SoC or wrong transition direction can leave wait-mode clocks misconfigured, affecting wakeup and low-power stability.

Test signals: i.MX6SL suspend/wait-mode entry and wake tests, clock register traces, and wake-source validation provide coverage.
