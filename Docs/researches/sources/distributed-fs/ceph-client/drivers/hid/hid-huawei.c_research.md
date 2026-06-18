# sources/distributed-fs/ceph-client/drivers/hid/hid-huawei.c

Provides a descriptor replacement for the Huawei CD30 keyboard. The fixed descriptor constrains consumer usages to `0x023c` and exposes system-control and consumer-control collections.

`huawei_cd30_kbd_rdesc_fixed` stores the replacement descriptor. `huawei_report_fixup()` checks product `USB_DEVICE_ID_HUAWEI_CD30KBD`, USB interface 1, and whether the current descriptor differs from the fixed descriptor. If replacement is needed, it updates `*rsize` and returns the fixed descriptor.

There is no private runtime state and no persistent device setting. The normal HID core path handles probe/start after report fixup. Dependencies include USB HID, report fixup hooks, and Huawei IDs from `hid-ids.h`.

Risks include static-descriptor assumptions and interface-number reliance. Test signals include CD30 interface 1 parsing, no replacement on interface 0, descriptor equality guard, consumer/system key behavior, and fallback on unexpected products.
