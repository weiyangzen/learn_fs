# sources/distributed-fs/ceph-client/arch/powerpc/platforms/82xx/km82xx.c

## Purpose
`km82xx.c` supports Keymile MGCOGE/KM82xx boards with CPM2 pinmux, clock routing, CPM2 PIC, and machine registration.

## Important APIs, Types, and Functions
`km82xx_pic_init()` finds `"fsl,pq2-pic"` and initializes CPM2 PIC. `init_ioports()` applies the board `km82xx_pins` table with `cpm2_set_pin()`, configures SMC/SCC/FCC clocks, and sets USB full-speed/slave-related IO data bits. `km82xx_setup_arch()` resets CPM2, applies the SIU18 snooping workaround, and initializes IO ports.

## Control Flow, State, and Persistence
The file persists no custom mappings; hardware state is programmed into CPM2 IO and clock registers during setup. The machine definition registers shared `pq2_restart()` and `cpm2_get_irq`.

## Dependencies and Integration Points
It depends on CPM2 core support, CPM2 PIC, OF `simple-bus` population, Keymile compatible `"keymile,km82xx"`, and `udbg_progress`.

## Risks and Test Signals
Risks include static pin tables not matching board revisions, CPM clock misrouting, and USB bit assumptions. Test signals are serial ports, SCC/FCC Ethernet, USB mode, CPM2 interrupts, simple-bus device creation, and restart.
