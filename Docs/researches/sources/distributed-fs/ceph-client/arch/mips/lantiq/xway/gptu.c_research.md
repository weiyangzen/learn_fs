# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/gptu.c

Purpose: exposes the XWAY GPTU six-timer block as clkdev-controllable timer clocks.

Important APIs/functions: `gptu_probe`, `gptu_enable`, `gptu_disable`, `timer_irq_handler`, `gptu_hwinit`, `gptu_hwexit`, `clkdev_add_gptu`, and `gptu_init`.

Control flow: `arch_initcall` registers a `lantiq,gptu-xway` platform driver. Probe collects six IRQ resources, maps MMIO, enables the parent clock, powers the GPTU, validates the magic ID byte, then registers six named clocks `timer1a` through `timer3b`. Enabling a timer requests its IRQ, configures count/edge/sync/internal clock mode, enables IRQ bit, and starts auto reload; disabling reverses those steps.

State and persistence: static MMIO base and six IRQ resources; per-timer state lives in GPTU registers and clkdev objects.

Dependencies and integration: depends on platform DT IRQ/resource tables, parent clock support from XWAY sysctrl, and the generic IRQ layer.

Risks: driver structure is named `dma_driver`, a misleading local name. `request_irq()` uses NULL dev_id, so shared IRQ use would be unsafe. Magic-ID failure disables hardware and returns `-ENAVAIL`.

Test signals: GPTU probe log, successful clk_get/enable for timer names, IRQ ack behavior, and timer disable cleanup.
