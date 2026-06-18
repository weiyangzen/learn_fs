# sources/distributed-fs/ceph-client/drivers/s390/net/smsgiucv.h

Purpose: provides the small public interface for the SMSGIUCV core driver.

Important APIs and types: defines `SMSGIUCV_DRV_NAME` as the IUCV driver name and declares `smsg_register_callback()` and `smsg_unregister_callback()`. The callback signature receives sender and mutable message text.

Control flow: no executable logic.

State and persistence: consumers depend on the core module retaining callback registrations until explicit unregister or module unload.

Dependencies and integration: included by `smsgiucv.c` and `smsgiucv_app.c`; the driver name is used by the app module to find the core IUCV driver.

Risks: there is no include guard in this header. It is currently simple enough not to matter in existing includes, but repeated inclusion could redeclare prototypes harmlessly and macro identically.

Test signals: compile coverage for core/app modules and symbol linkage for out-of-file callback users.
