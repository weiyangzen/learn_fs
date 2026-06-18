<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_embedded.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_embedded.h

Purpose: Declares embedded-platform convenience APIs for SSB watchdog and GPIO operations at the bus level.

Important APIs/types/functions: `ssb_watchdog_timer_set()`, `ssb_gpio_in()`, `ssb_gpio_out()`, `ssb_gpio_outen()`, `ssb_gpio_control()`, `ssb_gpio_intmask()`, and `ssb_gpio_polarity()`.

Control flow: Implementations elsewhere choose the appropriate underlying ChipCommon or EXTIF GPIO/watchdog backend for a given `ssb_bus`.

State and persistence behavior: Functions manipulate hardware watchdog and GPIO register state; no state is stored in this header.

Dependencies: `ssb.h` and `linux/types.h`.

Integration points: Embedded Broadcom board code, watchdog drivers, GPIO drivers, and platform initialization.

Risks: Bus-level helpers must serialize GPIO access using the locks held in `struct ssb_bus` or core-specific structs. Wrong backend selection can touch absent hardware.

Test signals: Embedded SSB builds, GPIO controller tests, watchdog timer tests, and boards with ChipCommon versus EXTIF GPIO backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_embedded.h -->
