# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/asus-wmi.h

## Purpose
`asus-wmi.h` is a Linux kernel x86 platform integration data header. It gives board files, MFD
children, ACPI glue, or platform-device setup code a compact contract for passing the primary type
`struct asus_hid_listener`; enumerations such as `enum asus_ally_mcu_hack`, `enum asus_hid_event`
into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_X86_ASUS_WMI_H`, `ASUS_WMI_MGMT_GUID`, `ASUS_ACPI_UID_ASUSWMI`,
`ASUS_WMI_METHODID_SPEC`, `ASUS_WMI_METHODID_SFBD`, `ASUS_WMI_METHODID_GLCD`,
`ASUS_WMI_METHODID_GPID`, `ASUS_WMI_METHODID_QMOD`, `ASUS_WMI_METHODID_SPLV`,
`ASUS_WMI_METHODID_AGFN`, `ASUS_WMI_METHODID_SFUN`, `ASUS_WMI_METHODID_SDSP`,
`ASUS_WMI_METHODID_GDSP`, `ASUS_WMI_METHODID_DEVP`, and 96 more. Types: `struct asus_hid_listener`,
`enum asus_ally_mcu_hack`, `enum asus_hid_event`. Declared or inline functions: `void`,
`set_ally_mcu_hack`, `set_ally_mcu_powersave`, `asus_wmi_get_devstate_dsts`,
`asus_wmi_set_devstate`, `asus_wmi_evaluate_method`, `asus_hid_register_listener`,
`asus_hid_unregister_listener`, `asus_hid_event`. Important struct details: struct asus_hid_listener
fields include `struct list_head list`, `void (*brightness_set)(struct asus_hid_listener *listener,
int brightness)`. Important enum details: enum asus_ally_mcu_hack values include
`ASUS_WMI_ALLY_MCU_HACK_INIT`, `ASUS_WMI_ALLY_MCU_HACK_ENABLED`, `ASUS_WMI_ALLY_MCU_HACK_DISABLED`;
enum asus_hid_event values include `ASUS_EV_BRTUP`, `ASUS_EV_BRTDOWN`, `ASUS_EV_BRTTOGGLE`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/asus-wmi.c`, `sources/distributed-fs/ceph-
client/drivers/platform/x86/asus-armoury.c`, `sources/distributed-fs/ceph-client/drivers/hid/hid-
asus.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/errno.h`, `linux/types.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/drivers/platform/x86/asus-wmi.c`, `sources/distributed-
fs/ceph-client/drivers/platform/x86/asus-armoury.c`, `sources/distributed-fs/ceph-
client/drivers/hid/hid-asus.c`. It integrates through `struct platform_device` platform data, board
files, MFD child registration, and legacy non-DT setup paths; many modern systems may replace parts
of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/asus-wmi.h` completely for this pass (232 lines, 8128 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/asus-wmi.h_research.md`.
