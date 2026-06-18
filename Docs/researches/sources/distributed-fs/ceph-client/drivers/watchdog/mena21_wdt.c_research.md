<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mena21_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/mena21_wdt.c`

Purpose: MEN A21 VME CPU board watchdog driver controlled entirely by six GPIO lines for enable, fast mode, trigger, and reset-cause inputs.

Important APIs, types, and functions: `struct a21_wdt_drv` stores watchdog core state and six GPIO descriptors. Start/stop set the enable GPIO, ping toggles trigger low then high with a 10 ns delay, set_timeout accepts only 1 or 30 seconds and controls the fast GPIO, and `a21_wdt_get_bootstatus()` reads three reset-status GPIOs.

Control flow: probe verifies exactly six GPIOs, acquires them by index, keeps initial values for output GPIOs, initializes static watchdog defaults, sets nowayout/drvdata/parent, maps reset bit patterns to bootstatus flags, stores driver data, and registers. Shutdown deasserts enable.

State and persistence: state is external board GPIO latch state; timeout mode is represented by the fast GPIO. Transition from 1-second fast mode back to 30-second slow mode is explicitly rejected. Bootstatus is decoded from reset GPIO combinations.

Dependencies and integration points: depends on OF compatible `men,a021-wdt`, GPIO descriptor ordering in devicetree, watchdog core, and board-specific reset-code wiring.

Risks and test signals: risks include GPIO ordering mistakes, static global watchdog object shared assumptions, fast-to-slow transition limitation, and no stop-on-reboot helper beyond shutdown. Test DT GPIO count/order, reset-code mappings, only accepted timeout values, trigger pulse visibility, shutdown disable, and nowayout behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/mena21_wdt.c -->
