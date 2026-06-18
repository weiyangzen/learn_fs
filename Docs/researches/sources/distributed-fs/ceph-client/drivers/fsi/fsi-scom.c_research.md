# sources/distributed-fs/ceph-client/drivers/fsi/fsi-scom.c

## Purpose
`fsi-scom.c` is the FSI client driver for the IBM FSI2PIB SCOM engine. It exposes each SCOM engine as an FSI character device named `scomN`, allowing userspace to read and write 64-bit SCOM registers by seeking to the target address and transferring exactly eight bytes, plus raw ioctl access for callers that need PIB and interface status details.

## Important APIs, Types, and Functions
The central state is `struct scom_device`, which owns the FSI device pointer, child `struct device`, `struct cdev`, a serialization mutex, and a `dead` flag used during removal. Low-level accessors are `__put_scom()` and `__get_scom()`, which program `SCOM_DATA0_REG`, `SCOM_DATA1_REG`, `SCOM_CMD_REG`, and read `SCOM_STATUS_REG`. Address routing is handled by `raw_put_scom()`, `raw_get_scom()`, `put_indirect_scom_form0()`, `put_indirect_scom_form1()`, and `get_indirect_scom_form0()`. User entry points are `scom_read()`, `scom_write()`, `scom_llseek()`, and `scom_ioctl()` for `FSI_SCOM_CHECK`, `FSI_SCOM_READ`, `FSI_SCOM_WRITE`, and `FSI_SCOM_RESET`.

## Control Flow
Probe allocates the device, takes a reference on the parent FSI device, allocates an FSI minor through `fsi_get_new_minor()`, initializes the cdev, and publishes it with `cdev_device_add()`. Normal read/write paths require `len == sizeof(u64)`, lock `scom->lock`, reject removed devices, and call the cooked `get_scom()` or `put_scom()` helpers. Cooked helpers invoke raw access, reset the bridge on FSI2PIB errors, then translate PIB response codes into Linux errors such as `-ENXIO`, `-ETIMEDOUT`, or `-EIO`.

Raw ioctls copy a `struct scom_access`, perform raw SCOM operations, and return decoded `pib_status` and `intf_errors` without converting every hardware status into a syscall failure. Raw writes support masked read-modify-write. Reset ioctl writes dummy data to the PIB and/or FSI2PIB reset registers according to user flags. Remove marks the device dead under the mutex, deletes the cdev, frees the minor, and drops the device reference.

## State and Persistence
There is no persistent storage. Runtime state is the character device lifetime, the FSI parent reference, and hardware engine registers. The mutex serializes all user operations and protects the `dead` flag so in-flight file operations cannot race a removed engine into further FSI access.

## Dependencies and Integration Points
The driver depends on the FSI core, FSI minor allocation, `fsi_cdev_type`, uapi definitions from `uapi/linux/fsi.h`, and device tree compatible `ibm,fsi2pib`. It binds FSI engine type `0x5` with any version.

## Risks and Test Signals
Indirect form1 reads are explicitly unsupported and return `-ENXIO`; userspace must handle that asymmetry. `scom_llseek()` returns the requested offset for `SEEK_CUR` without updating `file->f_pos`, which should be checked against expected chardev seek semantics. Raw masked writes skip the write if the preliminary read reports hardware status errors, but still return status to userspace. Tests should cover direct and indirect form0 accesses, masked raw writes, each PIB status mapping, reset flags, removal with open descriptors, and invalid transfer sizes.
