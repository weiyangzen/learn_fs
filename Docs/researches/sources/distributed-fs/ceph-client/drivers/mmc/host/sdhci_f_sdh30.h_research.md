# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci_f_sdh30.h

Purpose: this header defines the F_SDH30 vendor register offsets and bit fields used by `sdhci_f_sdh30.c` to configure AHB behavior, tuning, voltage switching, eMMC reset/HS200 mode, forced card insertion, and minimum clock.

Important APIs, types, and functions: it exposes register offsets `F_SDH30_AHB_CONFIG`, `F_SDH30_TUNING_SETTING`, `F_SDH30_IO_CONTROL2`, `F_SDH30_ESD_CONTROL`, and `F_SDH30_TEST`. Bit definitions include AHB endian/bus-lock/increment controls, command-check disable, voltage-switch control bits, eMMC reset, command/data delay, HS200 enable, forced card insert, and `F_SDH30_MIN_CLOCK`.

Control flow: the C driver includes this header and uses the definitions during probe-time vendor initialization, reset-time delay/card-detect handling, and soft voltage switching. There is no executable logic in the header.

State and persistence: the header itself stores no state. The constants identify hardware state persisted in vendor registers until reset, power loss, or explicit rewrite by the driver.

Dependencies and integration points: it assumes Linux `BIT()` is available through the including C file's headers. Its constants are tightly coupled to the F_SDH30 SDHCI wrapper and should not be used for generic SDHCI controllers.

Risks: incorrect bit definitions directly affect low-level electrical/timing behavior. Because the header has no include guard, duplicate inclusion in a broader translation unit would rely on identical macro definitions rather than guard protection, though current usage includes it once from the driver.

Test signals: compile coverage of `sdhci_f_sdh30.c`, register write traces during voltage switch and reset, and hardware tests confirming each vendor bit produces the expected controller behavior.
