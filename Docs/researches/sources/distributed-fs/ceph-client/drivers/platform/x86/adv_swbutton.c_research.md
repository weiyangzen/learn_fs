# sources/distributed-fs/ceph-client/drivers/platform/x86/adv_swbutton.c

Purpose: `adv_swbutton.c` is a compact Advantech ACPI software-button driver. It binds ACPI HID `AHC0310`, registers an input device named `Advantech Software Button`, and converts ACPI notify events into `KEY_PROG1` press/release input events.

Important APIs, types, and functions: `struct adv_swbutton` stores the devm-managed `input_dev` and a physical path string. `adv_swbutton_probe()` allocates state with `devm_kzalloc()`, allocates/registers an input device, enables device wakeup, and installs an ACPI device notify handler. `adv_swbutton_notify()` maps event `0x85` to key press and `0x86` to key release with `input_report_key()` and `input_sync()`. `adv_swbutton_remove()` removes the notify handler.

Control flow: platform-driver ACPI matching invokes probe. Probe registers input first, then ACPI notifications. Runtime ACPI notifications arrive with the platform device as context and report input events through the stored input device. Remove unregisters only the ACPI notify handler because devm owns memory and input-device lifetime.

State and persistence: state is per-device and volatile. Wakeup enablement is stored in the device power-management flags for the device lifetime. There is no firmware mutation beyond ACPI handler installation and no persistent data.

Dependencies and integration points: dependencies are ACPI, platform driver core, and input subsystem. The external ABI is an input event stream for `KEY_PROG1`; wakeup policy may also be visible via device power sysfs.

Risks: if `acpi_install_notify_handler()` fails after input registration, devm unwinds the input device but wakeup remains enabled until device cleanup. The handler assumes `dev_get_drvdata()` and `button->input` are valid, so notify removal ordering matters. Unknown ACPI events are ignored with debug logging only.

Test signals: bind on an ACPI node with HID `AHC0310`; verify `/proc/bus/input/devices` entry, press/release event reports for `0x85`/`0x86`, unsupported event debug behavior, and clean handler removal on driver unbind.
