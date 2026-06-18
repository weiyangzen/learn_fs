# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/dmi.c

Purpose: central DMI dispatch table for the x86 Android tablet fixup driver. It maps supported tablet DMI signatures to per-board `struct x86_dev_info` manifests defined in vendor files.

Important APIs and control flow: exports `x86_android_tablet_ids[]` and `MODULE_DEVICE_TABLE(dmi, ...)`. Entries include Acer, Advantech, Asus, Chuwi, Cyberbook, CZC/ViewSonic, Lenovo, Medion, Nextbook, Peaq, Vexia, Whitelabel, and Xiaomi devices. Many matches add BIOS date/version/SKU constraints where vendor/product strings are generic.

State and dependencies: no runtime state beyond the static table. It depends on extern `x86_dev_info` records from `acer.c`, `asus.c`, `lenovo.c`, and `other.c`, and is consumed by `dmi_first_match()` in `core.c`.

Risks and test signals: ordering is significant where generic matches could catch multiple tablets; comments call out cases like Lenovo Yoga Tablet 2 13-inch before 8/10-inch matches. Tests should verify modalias generation, DMI matching specificity, no accidental match broadening, and that every `driver_data` target is linked into the composite object.
