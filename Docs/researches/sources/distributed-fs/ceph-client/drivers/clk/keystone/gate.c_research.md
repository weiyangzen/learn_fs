# sources/distributed-fs/ceph-client/drivers/clk/keystone/gate.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/gate.c -->
## sources/distributed-fs/ceph-client/drivers/clk/keystone/gate.c

### Purpose
`gate.c` implements legacy Keystone PSC-based clock gates. It drives the Power Sleep Controller module/domain state machine so peripheral clocks can be enabled or disabled through common clock framework gate operations.

### Important APIs, Types, And Functions
Important types are `clk_psc_data` and `clk_psc`. Key functions are `psc_config()`, `keystone_clk_enable()`, `keystone_clk_disable()`, `keystone_clk_is_enabled()`, `clk_register_psc()`, `of_psc_clk_init()`, and `of_keystone_psc_clk_init()`. The OF compatible is `ti,keystone,psc-clock`.

### Control Flow, State, And Persistence
DT init maps `control` and `domain` register resources, reads `domain-id`, records domain transition base from domain zero, resolves parent and output name, registers a PSC clock, and adds a simple OF provider. Enabling/disabling takes the shared spinlock, programs MDCTL next state, optionally asserts local reset on disable, starts domain transition with PTCMD, polls PTSTAT, then polls MDSTAT until the requested state is reached.

### Dependencies, Integration Points, Risks, And Test Signals
The driver depends on DT `reg-names`, PSC register layout, parent clocks, and early OF clock declaration. Risks include no timeout error propagation from polling loops, global transition base depending on domain zero being initialized, missing parent causing failure, and register mapping leaks only handled on init failure. Test signals include enabling/disabling PSC modules, MDSTAT MCKOUT state, boot ordering with multiple domains, invalid DT resource tests, and peripheral functionality after clock transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/keystone/gate.c -->
