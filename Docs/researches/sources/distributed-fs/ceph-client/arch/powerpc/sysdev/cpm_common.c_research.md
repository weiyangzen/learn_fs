<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm_common.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm_common.c

Purpose: shared CPM support for MURAM initialization, optional early debug console output through CPM, and CPM/8xx GPIO chip registration helpers.

Important APIs/types/functions: `cpm_init()`, early-debug `udbg_init_cpm()`/`udbg_putc_cpm()`, GPIO structure `cpm2_gpio32_chip`, helper `cpm2_gpiochip_add32()`, and GPIO callbacks for get/set/direction.

Control flow: subsystem init looks for `fsl,cpm1` or `fsl,cpm2` and initializes CPM MURAM. Early debug maps the CPM transmit descriptor/buffer, optionally sets a BAT on CPM2, and installs `udbg_putc`. GPIO add allocates a gpiochip, maps the OF register bank, snapshots output data, and registers 32 GPIOs with locked data/direction operations.

State and persistence: early debug stores static descriptor/buffer pointers. GPIO state includes the mapped bank registers, a spinlock, and a shadow `cpdata` value used to update output bits safely. MURAM allocator state is initialized outside this file.

Dependencies and integration points: depends on OF compatible nodes, CPM MURAM, `asm/udbg.h`, fixmap/BAT helpers, GPIO subsystem, devm mapping/allocation, and CPM1/CPM2 register layouts.

Risks: early debug busy-waits on descriptor ownership and assumes valid firmware-provided descriptor addresses. GPIO shadow state can go stale if other code writes the same data register. CPM2 and 8xx layouts are conditionally shared, so compatible data must choose the right add function.

Test signals: CPM MURAM users probing successfully, early boot console output over CPM, GPIO direction/value operations through gpiolib, and no register corruption during concurrent GPIO updates validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm_common.c -->
