# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/common-board-devices.h

Purpose: Declares legacy common board-device support for OMAP N8x0 Menelaus platform data.

Important APIs/types/functions: Declares `n8x0_legacy_init()` and external `n8x0_menelaus_platform_data`.

Control flow: Header only; board/platform code includes it to initialize legacy N8x0 devices.

State and persistence: No local state. The external Menelaus platform data is defined elsewhere and persists as platform configuration.

Dependencies: Includes `<linux/mfd/menelaus.h>`.

Integration points: Connects OMAP2 board code to legacy Menelaus MFD platform data.

Risks: Legacy board-device interfaces can be configuration-sensitive and are unrelated to DT-centric CM code. Missing Menelaus support would break N8x0 legacy init.

Test signals: Build coverage for N8x0 legacy board configurations and platform device initialization.
