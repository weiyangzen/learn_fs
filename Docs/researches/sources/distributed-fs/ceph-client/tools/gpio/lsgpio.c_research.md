<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/lsgpio.c -->
# sources/distributed-fs/ceph-client/tools/gpio/lsgpio.c

Purpose: Lists GPIO chips and their lines, including names, consumers, flags, edge settings, and debounce attributes.

Important APIs/types/functions: `struct gpio_flag` and `flagnames[]` map GPIO v2 flags to text. `print_attributes()` prints flag and debounce attributes. `list_device()` opens `/dev/<gpiochip>`, issues `GPIO_GET_CHIPINFO_IOCTL`, then loops over line offsets with `GPIO_V2_GET_LINEINFO_IOCTL`. `main()` parses optional `-n` or scans `/dev` for `gpiochip*`.

Control flow: With `-n`, it lists exactly one chip. Without `-n`, it opens `/dev`, filters entries with `check_prefix()`, and lists each chip until failure, then closes the directory.

State and persistence: No persistent state. It opens each chip temporarily and prints inspection output.

Dependencies/integration: Depends on GPIO UAPI, `/dev/gpiochip*`, `gpio-utils.h` for `ARRAY_SIZE` and `check_prefix()`, and standard directory/ioctl APIs.

Risks/tests: Risks include races while scanning `/dev`, line info changing while listed, incomplete flag-name coverage for newer UAPI flags, and treating no devices as success after scan. Test signals are gpio-sim chips with named/unnamed lines, active-low/bias/edge/debounce flags, `-n` invalid device, and multi-chip scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/gpio/lsgpio.c -->
