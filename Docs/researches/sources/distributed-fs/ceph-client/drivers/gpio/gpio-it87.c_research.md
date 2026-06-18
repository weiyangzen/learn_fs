<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-it87.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-it87.c

## Purpose
`gpio-it87.c` exposes GPIO banks in ITE IT87xx Super I/O chips through legacy x86 I/O ports. It discovers the chip in Super I/O configuration mode, requests the runtime GPIO I/O window, and registers a dynamic gpiochip.

## Important APIs, types, and functions
`struct it87_gpio` stores the gpiochip, spinlock, runtime I/O base/size, output-enable register base, simple-I/O register base, and simple-I/O size. Low-level helpers enter/exit Super I/O config mode and read/write config registers. GPIO operations are `it87_gpio_request()`, get, direction input/output, and set. Module init/exit perform discovery and cleanup.

## Control flow
Module init reserves ports `0x2e/0x2f`, reads chip ID/revision, selects chip-specific register layout and line count, reads the GPIO base from logical device 7, requests the GPIO I/O region, allocates friendly line names, and registers the gpiochip. Request sets simple-I/O mode where available and defaults the line to input. Direction changes update Super I/O output-enable bits; values are read/written through the runtime GPIO I/O window.

## State and persistence behavior
Configuration persists in Super I/O registers until changed or reset. The driver does not shadow line values; it reads the I/O window. Allocated labels are kept through module lifetime and freed on exit.

## Dependencies and integration points
It uses legacy x86 port I/O, `request_muxed_region()` for Super I/O config access, `request_region()` for the GPIO window, and supports a fixed list of IT8613/8620/8628/8718/8728/8732/8761/8772/8786 IDs.

## Risks and edge cases
This is a singleton global module, not a platform driver. Unsupported chips fail hard. Some chips expose fewer physical lines than the convenient 64-line calculation, so unused exported lines may not behave as real pins. Direction changes require entering Super I/O mode and must be serialized.

## Test signals
Test chip discovery across supported IDs, region conflict handling, line naming, simple-I/O enable on supported chips, direction transitions, runtime I/O value get/set, and module unload freeing labels and regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-it87.c -->
