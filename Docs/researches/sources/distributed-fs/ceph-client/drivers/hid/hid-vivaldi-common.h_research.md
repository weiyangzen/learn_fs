# sources/distributed-fs/ceph-client/drivers/hid/hid-vivaldi-common.h

Purpose: small public header for the shared ChromeOS Vivaldi HID keyboard helpers.

Important APIs, types, and functions: forward-declares `struct hid_device`, `struct hid_field`, and `struct hid_usage`; declares `vivaldi_feature_mapping()` for use as a HID `feature_mapping` callback; declares exported `vivaldi_attribute_groups[]` for drivers that want the function-row sysfs attribute.

Control flow: none.

State and persistence: none directly. The declarations imply that callers provide HID drvdata compatible with `struct vivaldi_data` as required by the C implementation.

Dependencies and integration: included by `hid-vivaldi.c` and any other driver sharing Vivaldi function-row support. Keeps consumers from depending on implementation internals.

Risks: the header does not include `vivaldi-fmap.h`, so the drvdata layout requirement is not type-enforced here. Misuse by a driver with incompatible drvdata can corrupt reads in the common implementation.

Test signals: compile/link coverage through consumers. Runtime validation is reading the exported sysfs attribute on Vivaldi devices.
