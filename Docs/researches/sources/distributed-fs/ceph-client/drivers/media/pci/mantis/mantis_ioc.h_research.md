# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ioc.h

- Purpose: Defines GPIF GPIO line numbers, stream-routing enum, and IOC helper prototypes.
- Important APIs/types/functions: `GPIF_A00` through `GPIF_A14`, `enum mantis_stream_control`, `mantis_get_mac`, `mantis_gpio_set_bits`, `mantis_stream_control`.
- Control flow: Board configs reference GPIO numbers for power/reset and board callbacks invoke GPIO helpers; probe uses stream control and MAC read.
- State and persistence: No state; constants map to hardware lines.
- Dependencies and integration points: Integrated by board-specific frontend files and `mantis_cards.c`.
- Risks: GPIO constants are untyped and hardware-specific; wrong board config can drive incorrect lines.
- Test signals: Compile and board power/reset smoke tests.
