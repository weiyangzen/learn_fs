<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-gpio.c

## Purpose
`fsi-master-gpio.c` is a software bit-banged FSI master using GPIO lines. It serializes FSI protocol commands over clock/data/translator GPIOs, implements response parsing and retry behavior, and registers a single-link software-clocked master with the FSI core.

## Important APIs, types, and functions
`struct fsi_master_gpio` stores the embedded master, GPIO descriptors, command lock, external-mode flag, delay settings, and last-address cache. Protocol helpers include `serial_out()`, `serial_in()`, `clock_zeros()`, `msg_push_crc()`, `build_ar_command()`, `build_dpoll_command()`, `build_epoll_command()`, `read_one_response()`, `poll_for_response()`, and `fsi_master_gpio_xfer()`. Master callbacks are `fsi_master_gpio_read()`, `fsi_master_gpio_write()`, `fsi_master_gpio_term()`, `fsi_master_gpio_break()`, `fsi_master_gpio_link_enable()`, and `fsi_master_gpio_link_config()`.

## Control flow
Probe acquires mandatory clock/data GPIOs and optional trans/enable/mux GPIOs, sets default send/echo delays, marks the master as software-clocked, initializes GPIO output mode, creates `external_mode` sysfs, and registers the master. Reads and writes serialize on `cmd_lock`, build absolute/relative/same-address commands depending on `last_addr`, bit-bang the command with interrupts disabled around timing-sensitive serial I/O, wait through echo/send delays, parse ACK/BUSY/ERRA/ERRC responses, issue D_POLL or E_POLL retries, and update the last-address cache. BREAK clocks the protocol break sequence and invalidates the cache.

## State and persistence behavior
State is runtime-only: GPIO directions/values, `external_mode`, `last_addr`, and delay values. `external_mode` switches GPIOs to input/external mux mode and rescans the master; switching back reinitializes the bit-banged bus.

## Dependencies and integration points
It depends on GPIO descriptors, CRC4, IRQ flag helpers, delays, OF platform binding `fsi-master-gpio`, tracepoints, and the FSI master API. The FSI core uses its callbacks as a normal master and configures slave delays through `link_config`.

## Risks and edge cases
Timing is CPU/GPIO-controller dependent; `no-gpio-delays` improves AST2500 performance but can be unsafe elsewhere. The implementation disables local IRQs for serial segments but still relies on GPIO operations not sleeping. It supports only link 0. Response CRC retry and busy handling must avoid confusing command CRC errors with transport loss. Optional GPIOs must be present in practice for boards that need mux/translator control.

## Test signals
Signals include probe with and without optional GPIOs, FSI scan on link 0, reads/writes of 1/2/4 bytes, same/relative address command selection, CRC retry paths, BUSY D_POLL behavior, BREAK and TERM recovery, external-mode toggling, and timing behavior with `no-gpio-delays`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-gpio.c -->
