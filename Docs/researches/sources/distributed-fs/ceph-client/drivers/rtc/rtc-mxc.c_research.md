# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mxc.c

Purpose: supports older Freescale/NXP i.MX1 and i.MX21 RTC blocks with day/hour/minute/second counters, alarms, periodic interrupt bits, and clock-rate selection.

Important APIs/types/functions: `struct rtc_plat_data` stores RTC device, MMIO, IRQ, `ipg` and `ref` clocks, cached alarm time, and device type. `get_alarm_or_time()` and `set_alarm_or_time()` convert between split day/hour/min/sec registers and seconds. `rtc_update_alarm()` writes alarm registers and clears interrupt status. `mxc_rtc_irq_enable()` protects interrupt-enable updates with `rtc->irq_lock`. `mxc_rtc_interrupt()` handles alarm and periodic status.

Control flow: probe identifies i.MX1 versus i.MX21, maps MMIO, allocates RTC, sets range based on 9-bit or 16-bit days, enables `ipg` and `ref` clocks, validates the reference clock rate against supported values, enables the module, optionally requests a shared IRQ and wake IRQ, then registers. Reads repeat `get_alarm_or_time()` until two samples match. Set-time writes the split registers until a readback matches. Set-alarm clears status, writes alarm time, caches it, and enables/disables the alarm bit.

State and persistence: hardware persists split time/alarm counters, control, status, and interrupt enable bits. Driver state caches `g_rtc_alarm` but read-alarm gets hardware registers and pending status. For i.MX1, `start_secs` is initialized to the start of the current year unless DT overrides it.

Dependencies and integration: depends on OF compatibles `fsl,imx1-rtc` and `fsl,imx21-rtc`, named clocks `ipg` and `ref`, supported ref rates of 32768/32000/38400 Hz, optional shared IRQ, wake IRQ integration, and RTC class feature/range handling.

Risks and test signals: `mxc_rtc_interrupt()` takes `rtc->irq_lock` and calls `mxc_rtc_irq_enable()`, which takes the same spinlock again in the alarm path, a potential self-deadlock if the alarm bit is set. Read/write consistency loops have no timeout. IRQ absence still leaves alarm ops registered but no explicit feature clear. Test alarm IRQ path under lockdep, reference clock validation, no-IRQ platforms, i.MX1 start-time behavior, range limits, periodic status events, read/write rollover loops, and wake IRQ setup errors.
