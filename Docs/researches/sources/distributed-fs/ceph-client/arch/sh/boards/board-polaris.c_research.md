<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-polaris.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-polaris.c

Purpose: This file supports the SMSC Polaris SH7709 development board with SMSC911x Ethernet, heartbeat LEDs, wait-state setup, IPR IRQ mapping, and a machine vector.

Important APIs/types/functions: It defines bus-control macros, dummy supplies, SMSC911x resources/config/device, heartbeat data/resource/device, `polaris_devices`, `polaris_initialise`, IPR tables/offsets/descriptor, `init_polaris_irq`, and `mv_polaris`.

Control flow: `polaris_initialise` registers regulators/devices and programs area wait states for Ethernet. IRQ init registers IPR IRQ descriptors. The machine vector supplies the board name and IRQ callback.

State and persistence: Hardware wait-state register updates persist in the bus controller. Static device/platform data persists for Ethernet and LEDs.

Dependencies and integration points: It depends on SH7709, IPR interrupt support, fixed regulators, SMSC911x, heartbeat platform driver, and SuperH machine vectors.

Risks and test signals: Bus wait-state programming is needed for reliable Ethernet access. Tests include Ethernet register access/probe, heartbeat LEDs, IRQ handling, and boot with SH_POLARIS config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-polaris.c -->
