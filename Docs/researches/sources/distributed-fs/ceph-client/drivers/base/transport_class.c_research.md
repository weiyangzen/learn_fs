# sources/distributed-fs/ceph-client/drivers/base/transport_class.c

Purpose: this file implements generic transport class support on top of attribute containers, allowing subsystem transport-specific sysfs objects and attributes to be attached to generic devices.

Important APIs, types, and functions: exported APIs include `transport_class_register`, `transport_class_unregister`, `anon_transport_class_register`, `anon_transport_class_unregister`, `transport_setup_device`, `transport_add_device`, `transport_configure_device`, `transport_remove_device`, and `transport_destroy_device`. Internal callbacks include `transport_setup_classdev`, `transport_add_class_device`, `transport_configure`, `transport_remove_classdev`, and `transport_destroy_classdev`.

Control flow: class registration wraps `class_register`/`class_unregister`. Anonymous transport classes configure an attribute container with no class devices and dummy setup/remove functions. Device setup triggers matching containers to allocate/initialize class devices. Add makes class devices visible, then adds optional statistics and encryption sysfs groups. Configure invokes the transport class's `configure` callback. Remove invokes the class `remove`, removes optional groups, and deletes the class device. Destroy drops the class-device reference for non-anonymous classes.

State and persistence: transport class/container state is owned by callers. This file creates and removes sysfs visibility and class-device references through attribute-container infrastructure but does not maintain a separate global list.

Dependencies and integration points: it depends on `linux/attribute_container.h`, `linux/transport_class.h`, sysfs groups, class devices, and subsystem-specific transport classes such as SCSI transport layers.

Risks: lifecycle ordering matters: setup, add, configure, remove, and destroy are intentionally separate. Missing remove/destroy leaves sysfs objects or references behind. Error paths in add must remove partially added class devices and call transport `remove`. Anonymous transport classes rely on the dummy function sentinel to skip normal class-device deletion.

Test signals: subsystem tests should verify sysfs attributes appear after add, optional groups are removed on failure and removal, configure callbacks run after setup, and destroy releases references. Fault injection around `attribute_container_add_class_device` and `sysfs_create_group` is useful.
