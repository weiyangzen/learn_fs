<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_extif.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_extif.h

Purpose: Describes the SSB External Interface core used on BCM47xx-family chips for external chip selects, PCMCIA/flash/asynchronous devices, UARTs, watchdog, clocking, and GPIO.

Important APIs/types/functions: `SSB_EXTIF_*` address/register/bit constants, GPIO register offset macros with `BUILD_BUG_ON`, wait-count fields, watchdog clock limits, `struct ssb_extif`, `ssb_extif_available()`, clock/timing/watchdog helpers, GPIO helpers, and optional serial init.

Control flow: When `CONFIG_SSB_DRIVER_EXTIF` is enabled, callers operate on a real `struct ssb_extif` containing an SSB device and GPIO lock. When disabled, the same API compiles to safe stubs returning false, zero, or success as appropriate.

State and persistence behavior: Hardware state is in EXTIF registers for chip-select configuration, wait counts, watchdog timer, clock dividers, UART, and GPIO. In-memory state is the core device pointer and GPIO lock.

Dependencies: SSB device accessors, spinlocks, serial port definitions if serial is enabled, and compile-time SSB driver configuration.

Integration points: Board flash, PCMCIA, external UART/Bluetooth, GPIO, and watchdog support on SSB embedded platforms.

Risks: Wait-count and chip-select programming is timing-sensitive; incorrect GPIO index usage is prevented at compile time only for constant indexes. Disabled stubs can hide missing hardware support if callers do not check availability.

Test signals: EXTIF-enabled and disabled builds, GPIO register access tests, watchdog maximum tests, flash/PCMCIA timing validation, and serial initialization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_extif.h -->
