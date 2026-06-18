# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_hif_dpmaif.c

Purpose: orchestrates the t7xx DPMAIF data path above the register layer, tying RX/TX software resources, hardware initialization, PCIe interrupts, modem state callbacks, and PM callbacks together.

Important APIs/functions: `t7xx_dpmaif_hif_init()` allocates `dpmaif_ctrl`, registers PM entity, registers PCIe IRQ handlers, allocates RX/TX software rings/workers, and returns the controller. `t7xx_dpmaif_start()` builds `dpmaif_hw_params` from allocated queues, allocates initial BAT/frag buffers, initializes hardware, gives BAT counts to hardware, clears interrupts, marks state `PWRON`, enables IRQs, and wakes TX. `t7xx_dpmaif_irq_cb()` converts hardware interrupt events into TX done or RX NAPI scheduling and error logging/unmasking. `t7xx_dpmaif_md_state_callback()` starts or stops DPMAIF based on modem state. Suspend/resume callbacks stop/start queues and interrupts.

Control flow and state: `dpmaif_ctrl->state` gates interrupts and lifecycle. `dpmaif_sw_init_done` gates exit. RX queues use `DPMAIF_INT`/`DPMAIF2_INT`; IRQ top halves mask PCIe INT and threaded handlers do decode/unmask. Software allocation creates shared BAT resources, RX queues, TX queues, TX thread, and BAT release workqueue.

Dependencies and integration points: depends on DPMAIF hardware layer, DPMAIF RX/TX helpers, t7xx PCIe MAC interrupt plumbing, t7xx PM entity registration, state monitor, and network callbacks.

Risks and test signals: error unwinding around shared BAT freeing, interrupt state before `PWRON`, modem exception/stop races, and suspend/resume queue state are key risks. Test modem boot/exception/stop, IRQ storms, PM cycles, and allocation-failure paths.
