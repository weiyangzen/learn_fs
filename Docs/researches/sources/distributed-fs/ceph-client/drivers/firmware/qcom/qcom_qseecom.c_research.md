# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_qseecom.c

## Purpose
`qcom_qseecom.c` is a small platform driver that turns loaded Qualcomm SEE applications into Linux auxiliary devices. It currently detects `qcom.tz.uefisecapp` and registers a `qcom_qseecom.uefisecapp` auxiliary client when the secure app is present.

## Important APIs, Types, And Functions
- `struct qseecom_app_desc` maps secure app names to auxiliary device names.
- `qseecom_client_register()` calls `qcom_scm_qseecom_app_get_id()`, allocates `struct qseecom_client`, initializes `auxiliary_device`, and registers devm cleanup.
- `qseecom_client_release()` and `qseecom_client_remove()` handle auxiliary lifetime.
- `qcom_qseecom_probe()` loops over `qcom_qseecom_apps`.
- `subsys_initcall(qcom_qseecom_init)` registers the platform driver named `qcom_qseecom`.

## Control Flow
SCM creates the parent platform device only on supported machines after QSEECOM version probing. This driver then probes that device, queries each configured secure app by name, skips absent apps with success, and creates an auxiliary device for present apps. Auxiliary client drivers match names such as `qcom_qseecom.uefisecapp` and use the stored app ID to send requests.

## State And Persistence
Per-client state is the allocated `struct qseecom_client` containing the app ID and embedded auxiliary device. The lifetime is tied to the parent platform device through `devm_add_action_or_reset()`. There is no persistent storage.

## Dependencies And Integration Points
The driver depends on `qcom_scm_qseecom_app_get_id()` from SCM, the auxiliary bus, and `linux/firmware/qcom/qcom_qseecom.h` for the client type. It is the bridge between SCM's generic QSEECOM transport and concrete auxiliary client drivers.

## Risks
Only already-loaded secure apps are discovered; firmware/bootloader load order controls device presence. Any non-`ENOENT` lookup error fails the whole probe. Auxiliary lifetime must call both `auxiliary_device_delete()` and `auxiliary_device_uninit()` to avoid leaks.

## Test Signals
A successful app discovery logs setup for the app and creates an auxiliary device matching the client driver's ID table. Absent apps should not fail probe. The UEFI secure app driver probing is the main downstream integration signal.
