# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/espi.c

## Purpose
`espi.c` implements Ethernet SPI4/ESPI initialization, interrupt accounting, and monitor-counter access for Chelsio T1/T2 adapters. It programs ESPI calendars, FIFO watermarks, burst sizes, training, port counts, and T2 TRICN settings according to the attached MAC type and number of ports.

## Important APIs, Types, and Functions
The private `struct peespi` stores the adapter pointer, `struct espi_intr_counts`, a shadow `misc_ctrl`, and a lock for monitored-counter selection. Public APIs are `t1_espi_create()`, `t1_espi_destroy()`, `t1_espi_init()`, `t1_espi_intr_enable()`, `t1_espi_intr_disable()`, `t1_espi_intr_clear()`, `t1_espi_intr_handler()`, `t1_espi_get_intr_counts()`, `t1_espi_get_mon()`, and `t1_espi_get_mon_t204()`.

Key private helpers include `tricn_write()` and `tricn_init()` for T2 TRICN register programming, plus `espi_setup_for_pm3393()`, `espi_setup_for_vsc7321()`, and `espi_setup_for_ixf1010()` for MAC-specific ESPI setup.

## Control Flow
Creation allocates and binds a `peespi` to an adapter. `t1_espi_init()` disables training by default, programs T2 or T1 burst/misc thresholds, dispatches to a MAC-specific setup routine, enables RX FIFO status, and for T2 initializes TRICN plus monitor-counter selection. Interrupt enable masks ESPI drops/parity/DIP errors except on T1B where a documented hardware bug prevents reliable clearing. The interrupt handler reads `A_ESPI_INTR_STATUS`, increments software counters for each asserted cause, reads the DIP2 error count when needed to clear that source, writes back the appropriate status value, and returns.

Monitor reads use `A_ESPI_MISC_CONTROL` to select the requested port/direction/interface and read `A_ESPI_SCH_TOKEN3`. `t1_espi_get_mon()` supports single-port monitored counters with optional trylock behavior; `t1_espi_get_mon_t204()` reads all T204 ingress TX SOP counters while preserving the shadow control value.

## State and Persistence
Persistent hardware state includes ESPI FIFO thresholds, calendar length, port count, training/burst settings, interrupt enable bits, and misc monitor selection. Software state is limited to accumulated interrupt counters and `misc_ctrl`. No data survives driver unload or hardware reset.

## Dependencies and Integration Points
The file depends on `common.h`, `regs.h`, and `espi.h`. It is called during hardware initialization from the common module setup path and observed by `cxgb2.c` ethtool statistics through `t1_espi_get_intr_counts()`. `sge.c` uses `t1_espi_get_mon()` and `t1_espi_get_mon_t204()` for the T2 stuck-packet workaround. Interrupt control integrates with the PL interrupt registers `A_PL_ENABLE` and `A_PL_CAUSE`.

## Risks
Risks are hardware-revision sensitive. Enabling ESPI interrupts on T1B can create unclearable interrupts, so the mask must remain conditional. Wrong MAC type or port count programming can break SPI4 framing or FIFO scheduling. Monitor-counter reads temporarily rewrite `A_ESPI_MISC_CONTROL`; missing locking would corrupt concurrent workaround reads. TRICN writes poll only a bounded number of attempts, so timeout handling is limited to error logging and a busy return.

## Test Signals
Test signals include successful adapter initialization for PM3393, VSC7321, and IXF1010 boards; correct interrupt counters under induced DIP/drop/parity events; no ESPI interrupt storm on T1B; T2 TRICN initialization only after RX clock-ready; stable `ethtool -S` ESPI counters; and T204 stuck-packet workaround monitor reads that do not race or leave `A_ESPI_MISC_CONTROL` misselected.
