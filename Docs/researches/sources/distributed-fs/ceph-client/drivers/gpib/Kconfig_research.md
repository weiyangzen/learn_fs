# sources/distributed-fs/ceph-client/drivers/gpib/Kconfig

## Purpose
This Kconfig file defines a set of Linux GPIB adapter drivers and hidden helper modules for the GPIB subsystem.

## Important Entries
Top-level `GPIB` enables the menu. `GPIB_COMMON` provides the core userspace interface. Board drivers include Agilent 82350B PCI, Agilent 82357A USB, CEC PCI, NI PCI/ISA/TNT, CB7210, NI USB, Fluke, FMH, GPIO bitbang, HP82335, HP82341, INES, LPVO, and PC2. Hidden helpers include `GPIB_TMS9914`, `GPIB_NEC7210`, and `GPIB_PCMCIA`.

## Control Flow and State
There is no runtime flow. Kconfig dependencies select common bus, IO port, PCI, USB, OF, ISA, and PCMCIA support as needed.

## Dependencies and Integration Points
Most board drivers select `GPIB_COMMON` plus a chip helper such as `GPIB_NEC7210` or `GPIB_TMS9914`. Userspace integration is through the linux-gpib library mentioned in help text.

## Risks and Test Signals
The help text has rough edges, including a `called cb7210` line appearing under the INES entry after the CB7210 entry, which can confuse menu help. The `depends on PCMCIA || !PCMCIA` pattern is used to force visibility across PCMCIA states. Test signals are Kconfig lint, allmodconfig, and per-driver dependency builds on platforms with and without IO ports.
