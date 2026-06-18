# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-spi.c

## Purpose
Implements low-level SPI4 bring-up and restart for CN38XX/CN58XX through a callback-driven sequence.

## Important APIs, Types, And Functions
APIs include `cvmx_spi_get_callbacks()`, `cvmx_spi_set_callbacks()`, `cvmx_spi_start_interface()`, `cvmx_spi_restart_interface()`, and default reset/calendar/clock/training/sync/interface-up callbacks.

## Control Flow
Start runs reset, calendar setup, clock detection, training, calendar sync, and interface-up callbacks, aborting on nonzero return. Restart skips calendar setup. Reset masks interrupts, runs BIST, clears calendars, configures clocks/DLL and dynamic alignment. Calendar setup fills RX/TX round-robin calendars. Clock/training/sync stages poll CSR status with timeouts. Interface-up enables SRX/STX and programs GMX frame bounds.

## State, Persistence, And Dependencies
State is in SPXX/SRXX/STXX/GMX CSRs and in the global callback table. Timing uses CPU cycle counts and `cpu_clock_hz`.

## Integration Points
`cvmx-helper-spi.c` calls `cvmx_spi_start_interface()` during SPI enable. Boards may replace callbacks.

## Risks
Callback replacement is global and unsynchronized. BIST failures print but do not abort. Several loops can take long or timeout.

## Test Signals
Check BIST output, clock-detect timeout, training completion, calendar sync, interface-up messages, restart after link loss, and callback-abort behavior.
