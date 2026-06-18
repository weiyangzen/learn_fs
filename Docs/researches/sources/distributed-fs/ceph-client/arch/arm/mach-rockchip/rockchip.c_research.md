# sources/distributed-fs/ceph-client/arch/arm/mach-rockchip/rockchip.c

Purpose: Rockchip DT machine descriptor and early timer/suspend initialization.

Important APIs/types/functions: `rockchip_timer_init()`, `rockchip_dt_init()`, compatible table for RK2928/RK3066/RK3188/RK3228/RK3288/RV1108, and `DT_MACHINE_START(ROCKCHIP_DT)`.

Control flow: timer init special-cases RK3288 by mapping timer6/7 and enabling timer7 for the architected timer before calling `of_clk_init()` and `timer_probe()`. Machine init calls `rockchip_suspend_init()`.

State and persistence: temporarily maps timer registers and writes timer count/control values. No long-lived local state.

Dependencies and integration points: integrates common clock/timer DT probing, RK3288 bootloader workaround, and PM initialization.

Risks: fixed RK3288 physical timer address must be valid. If mapping fails, boot continues with an error and architected timer may not work.

Test signals: early clocksource availability, RK3288 timer workaround logs, DT compatible matching, and suspend ops registration.
