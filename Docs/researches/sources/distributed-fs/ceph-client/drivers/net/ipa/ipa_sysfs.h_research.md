# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_sysfs.h

Purpose: declares the sysfs attribute groups registered by the IPA platform driver.

Important APIs/data: extern declarations for the base IPA attribute group, feature group, endpoint ID group, and legacy modem group.

Control flow: `ipa_main.c` includes this header and installs the groups in the platform driver's `dev_groups`; `ipa_sysfs.c` provides the definitions and show callbacks.

State/persistence: no state is defined here. Attribute values are computed dynamically from `struct ipa`.

Dependencies/integration: relies on Linux `struct attribute_group` being visible through included sysfs/device headers in users.

Risks: adding/removing groups requires coordinating this header, definitions, and platform-driver group list.

Test signals: driver builds with all externs resolved and sysfs group registration succeeds during platform device creation.
