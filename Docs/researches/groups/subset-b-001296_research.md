# Research Group: subset-b-001296

Grouped research for the assigned FSI, fwctl, GNSS, and GPIB driver sources. Each file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-scom.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-scom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-slave.h -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-slave.h

## Purpose
`fsi-slave.h` is a private FSI core header that defines the in-kernel representation of an FSI slave device. It is used by FSI client and master-adjacent code that needs to reach from `struct device` or an FSI device to slave addressing and parent-master details.

## Important APIs, Types, and Functions
The file defines `struct fsi_slave` with embedded `struct device dev`, parent `struct fsi_master *master`, character-device state, FSI address and link identifiers, `cfam_id`, `chip_id`, address-space `size`, and timing fields `t_send_delay` and `t_echo_delay`. The only helper is `to_fsi_slave(d)`, a `container_of()` conversion from the embedded device.

## Control Flow
There is no runtime control flow in this header. It defines shared layout consumed by FSI core and client drivers. In this work item, `i2cr-scom.c` uses `fsi_dev->slave->master` to confirm that the SCOM client is attached under an I2CR FSI master.

## State and Persistence
The structure is runtime kernel state. It is not persisted and does not define locking; users rely on the FSI core's object lifetime rules.

## Dependencies and Integration Points
The header depends on Linux `device` and `cdev` types and forward-declares `struct fsi_master`. It is intentionally local to `drivers/fsi`, not a UAPI contract.

## Risks and Test Signals
Because users dereference `slave->master`, lifetime and initialization ordering are important. Any future layout changes must be coordinated with all FSI client drivers. Test signals are compile coverage of FSI clients, hotplug/remove paths that free slaves, and lockdep or KASAN findings around master/slave lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-slave.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/i2cr-scom.c -->
# sources/distributed-fs/ceph-client/drivers/fsi/i2cr-scom.c

## Purpose
`i2cr-scom.c` exposes an IBM I2C Responder SCOM device as the same FSI character-device class used by normal SCOM, but it routes 64-bit register reads and writes through the I2CR FSI master helper instead of directly programming the FSI2PIB SCOM engine.

## Important APIs, Types, and Functions
`struct i2cr_scom` holds the child device, cdev, and `struct fsi_master_i2cr *`. File operations are `i2cr_scom_read()`, `i2cr_scom_write()`, and `i2cr_scom_llseek()`, with `simple_open` setting private data through the cdev helper. Probe uses `is_fsi_master_i2cr()`, `to_fsi_master_i2cr()`, `fsi_get_new_minor()`, and `cdev_device_add()`. The transport calls are `fsi_master_i2cr_read()` and `fsi_master_i2cr_write()`.

## Control Flow
Probe rejects devices whose slave master is not an I2CR master. It allocates private state with devres, stores the I2CR master pointer, initializes a child FSI cdev, allocates an FSI SCOM minor, and publishes `scomN`. Reads and writes require exactly eight bytes, cast the current file offset to a 32-bit address, and delegate to the I2CR master read/write operation before copying data to or from userspace. Remove deletes the cdev and frees the minor.

## State and Persistence
State is limited to the character device, minor number, and cached I2CR master pointer. The file has no explicit lock or `dead` flag; cdev removal and FSI device lifetime rules provide the safety boundary.

## Dependencies and Integration Points
The driver depends on `fsi-master-i2cr.h`, private `fsi-slave.h`, the FSI cdev type and minor allocator, and OF compatible `ibm,i2cr-scom`. It binds engine type `0x5` with any version.

## Risks and Test Signals
The offset is truncated to `u32`, so callers cannot address beyond the I2CR helper's 32-bit register space through this device. Unlike `fsi-scom.c`, there are no raw status ioctls, masking, reset handling, or mutex serialization. `copy_to_user()` and `copy_from_user()` return byte counts, but this code returns that value directly rather than normalizing to `-EFAULT`, which is worth checking against kernel style. Tests should cover non-I2CR probe rejection, basic read/write, invalid lengths, minor cleanup on `cdev_device_add()` failure, and disconnect while userspace holds a file descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/i2cr-scom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/fwctl/Kconfig

## Purpose
This Kconfig file introduces the fwctl firmware-access framework and its first device-specific providers. The framework is intended to provide a restricted userspace path for device firmware communication that does not fit existing subsystems.

## Important Entries
`FWCTL` is the top-level tristate menuconfig. Provider symbols are `FWCTL_BNXT`, `FWCTL_MLX5`, and `FWCTL_PDS`, depending respectively on `BNXT`, `MLX5_CORE`, and `PDS_CORE`.

## Control Flow and State
There is no runtime code. Kconfig selection controls whether the core `fwctl` module and each auxiliary-bus provider module are built.

## Dependencies and Integration Points
The entries integrate with NIC core drivers that create auxiliary devices. The runtime subsystem also relies on uapi headers under `uapi/fwctl`.

## Risks and Test Signals
The top-level help text describes powerful firmware operations including flash manipulation and debugging, so build enablement should be reviewed with lockdown and privilege expectations. Tests are mainly configuration matrix builds: core alone, each provider as built-in or module, and provider symbols disabled when their parent NIC symbols are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/fwctl/Makefile

## Purpose
This Makefile wires the fwctl core and provider subdirectories into Kbuild.

## Important Entries
`obj-$(CONFIG_FWCTL) += fwctl.o` builds the core from `main.o`. Provider directories are included for `CONFIG_FWCTL_BNXT`, `CONFIG_FWCTL_MLX5`, and `CONFIG_FWCTL_PDS`.

## Control Flow and State
There is no runtime control flow. The file affects object selection and link composition.

## Dependencies and Integration Points
The provider directories each produce their own module object and import the fwctl namespace exported by the core.

## Risks and Test Signals
Build failures here would appear as missing provider objects or unresolved fwctl symbols. Test signals are allmodconfig and per-provider modular builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/bnxt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/fwctl/bnxt/Makefile

## Purpose
This Kbuild file builds the Broadcom BNXT fwctl provider.

## Important Entries
`obj-$(CONFIG_FWCTL_BNXT) += bnxt_fwctl.o` and `bnxt_fwctl-y += main.o` map the Kconfig symbol to the provider implementation.

## Control Flow and State
No runtime behavior is defined here.

## Dependencies and Integration Points
The object depends on the parent `bnxt_en` driver infrastructure and the fwctl core namespace.

## Risks and Test Signals
Configuration-only risks include provider build breakage when BNXT internal headers change. Test with `FWCTL_BNXT=m` and parent BNXT built as both module and built-in where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/bnxt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/bnxt/main.c -->
# sources/distributed-fs/ceph-client/drivers/fwctl/bnxt/main.c

## Purpose
`bnxt/main.c` is the Broadcom BNXT fwctl provider. It exposes selected HWRM firmware commands to userspace through the fwctl core, while validating each request against an allowlist and the requested fwctl RPC scope.

## Important APIs, Types, and Functions
`struct bnxtctl_dev` embeds `struct fwctl_device` and stores `struct bnxt_aux_priv *`. `struct bnxtctl_uctx` embeds `struct fwctl_uctx` and per-open capability bits. fwctl callbacks are `bnxtctl_open_uctx()`, `bnxtctl_close_uctx()`, `bnxtctl_info()`, and `bnxtctl_fw_rpc()`. The critical policy functions are `bnxtctl_validate_rpc()` and `bnxtctl_get_timeout()`.

## Control Flow
The auxiliary driver binds `bnxt_en.fwctl`. Probe allocates an fwctl device against the PCI parent, stores the BNXT aux private pointer, registers with fwctl, and stores driver data. Open sets capability bits for inline, query, and send commands. Info returns those caps in `struct fwctl_info_bnxt`.

RPC handling validates request and response sizes against HWRM structures, allocates a response buffer of the caller-requested size, chooses a timeout based on command type, and takes `edev->en_dev_lock`. Validation rejects stopped ULP state and allows only specific HWRM request types, with configuration, debug-read, and debug-write scope thresholds. `bnxt_send_msg()` sends the message. If firmware returns detailed status while the send function returns an error, the provider still returns the response buffer to userspace and fills `error_code` when needed.

## State and Persistence
Per-open state is only capability bits. Device state is the fwctl object and the BNXT auxiliary pointer. There is no persistent storage. The BNXT lock serializes firmware message submission against device state.

## Dependencies and Integration Points
The driver depends on `linux/bnxt/hsi.h`, `linux/bnxt/ulp.h`, auxiliary bus, PCI parent devices, fwctl core, and uapi `fwctl/bnxt.h`. It imports namespace `FWCTL`.

## Risks and Test Signals
The security boundary is the HWRM allowlist and scope mapping, so new firmware commands require careful classification. Default rejection is good, but command aliases or structure changes can invalidate assumptions. Response-size handling trusts userspace to provide at least `sizeof(struct output)` while still passing the full requested size to firmware. Tests should exercise each allowed scope, denied command IDs, ULP-stopped rejection, long-timeout NVM commands, firmware error responses, and remove while fds remain open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/bnxt/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/main.c -->
# sources/distributed-fs/ceph-client/drivers/fwctl/main.c

## Purpose
`fwctl/main.c` implements the fwctl character-device core. It provides `/dev/fwctl/fwctlN` devices, per-file user contexts owned by provider drivers, ioctl dispatch for info and firmware RPC commands, lifetime disassociation on unregister, and global tainting for write-capable debug access.

## Important APIs, Types, and Functions
Important internal types are `struct fwctl_ucmd` and `struct fwctl_ioctl_op`. Public provider APIs are `_fwctl_alloc_device()`, `fwctl_register()`, and `fwctl_unregister()`. File operations are `fwctl_fops_open()`, `fwctl_fops_release()`, and `fwctl_fops_ioctl()`. Command handlers are `fwctl_cmd_info()` and `fwctl_cmd_rpc()`. Helpers include `ucmd_respond()` and `copy_to_user_zero_pad()`.

## Control Flow
Subsystem init allocates up to 4096 character minors and registers class `fwctl` with devnodes under `fwctl/`. Providers allocate devices through the wrapper around `_fwctl_alloc_device()`, which allocates a class device, cdev, locks, and a list of open contexts. `fwctl_register()` publishes the cdev.

Open takes `registration_lock` for reading, rejects unregistered devices, allocates the provider-defined `uctx_size`, calls `ops->open_uctx()`, adds the context to the device list, takes a device reference, and stores it in `filp->private_data`. Ioctl dispatch validates the ioctl number, user-provided struct size, and minimum trailing field through `copy_struct_from_user()`, then executes under the registration read lock. Info optionally calls provider `info()`, copies provider data to the user buffer with zero padding, and returns device type plus actual length. RPC enforces a 2 MiB input and output cap, maps fwctl scopes, requires `CAP_SYS_RAWIO` for `FWCTL_RPC_DEBUG_WRITE_FULL`, taints the kernel for debug write scopes, copies input, calls provider `fw_rpc()`, copies output, and returns actual output length.

Unregister deletes the cdev, takes the write lock, destroys all open user contexts by calling provider `close_uctx()`, then sets `ops = NULL` so remaining file descriptors return `-ENODEV`. Release only calls provider close if unregister has not already done so.

## State and Persistence
State is volatile: IDA minor allocation, class device lifetime, open-context list, locks, and a global `fwctl_tainted` bit used to emit one warning and add `TAINT_FWCTL`. No firmware messages are persisted by the core.

## Dependencies and Integration Points
The core depends on fwctl uapi structs, cdev/class infrastructure, `copy_struct_from_user()`, `cleanup.h` scoped guards, kernel capabilities, and module namespace exports. Provider drivers supply `struct fwctl_ops`.

## Risks and Test Signals
The core is the lifetime and policy boundary. Provider `fw_rpc()` may return the input buffer as output, and the core must avoid double-freeing by nulling `inbuf`; this path is present and should be tested. Pointer arithmetic on `void __user *` in zero padding relies on compiler extension accepted by the kernel. Tests should cover ioctl struct size compatibility, zero padding for short provider info, all scope permission paths, `MAX_RPC_LEN` rejection, provider output shorter and longer than requested, unregister with open fds, and release after unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/mlx5/Makefile -->
# sources/distributed-fs/ceph-client/drivers/fwctl/mlx5/Makefile

## Purpose
This Kbuild file builds the mlx5 fwctl provider.

## Important Entries
`obj-$(CONFIG_FWCTL_MLX5) += mlx5_fwctl.o` and `mlx5_fwctl-y += main.o` map the provider symbol to its implementation.

## Control Flow and State
There is no runtime flow or persistent state in this file.

## Dependencies and Integration Points
The object depends on mlx5 core headers and the fwctl exported namespace.

## Risks and Test Signals
Build tests should cover modular and built-in mlx5 configurations and verify `MODULE_IMPORT_NS("FWCTL")` resolves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/mlx5/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/mlx5/main.c -->
# sources/distributed-fs/ceph-client/drivers/fwctl/mlx5/main.c

## Purpose
`mlx5/main.c` is the Mellanox/NVIDIA mlx5 fwctl provider. It creates a firmware user context UID per open file and allows a curated set of mlx5 command-interface messages to be sent through the fwctl RPC path.

## Important APIs, Types, and Functions
`struct mlx5ctl_dev` embeds `struct fwctl_device` and stores the `mlx5_core_dev`. `struct mlx5ctl_uctx` stores the fwctl context, capabilities, and firmware UID. Important helpers are `mlx5ctl_alloc_uid()`, `mlx5ctl_release_uid()`, `mlx5ctl_open_uctx()`, `mlx5ctl_close_uctx()`, `mlx5ctl_info()`, `mlx5ctl_validate_rpc()`, and `mlx5ctl_fw_rpc()`.

## Control Flow
Probe binds an mlx5 auxiliary device named `mlx5_core.fwctl`, allocates an fwctl device under the PCI parent, and registers it. On each open, the driver checks whether firmware supports the `TOOLS_RESOURCES` UCTX capability, allocates a UID via `CREATE_UCTX`, and stores it in the user context. Close destroys that UID. Info returns the UID and capability bits.

RPC validation checks minimum mailbox header sizes, logs opcode and buffer sizes, rejects commands outside the allowlist, allocates an output buffer unless the input buffer can be reused, writes the per-open UID into the mailbox header, and executes the command with `mlx5_cmd_do()`. `-EREMOTEIO` is treated as a valid device-level command response with an error status inside the output buffer; other errors free the output and return an errno.

## State and Persistence
The persistent-for-open state is the firmware UID, which is destroyed on close or unregister. There is no on-disk state. Device state is the registered fwctl object and the mlx5 core pointer.

## Dependencies and Integration Points
The driver depends on mlx5 command definitions, mlx5 auxiliary device plumbing, fwctl core, and `uapi/fwctl/mlx5.h`. It imports namespace `FWCTL` and uses dual BSD/GPL licensing.

## Risks and Test Signals
The command allowlist is the main safety control. Some configuration-class cases currently return true without checking the requested scope, as indicated by commented `scope >= FWCTL_RPC_CONFIGURATION` notes; that behavior should be intentional and tested. Object-allocating commands are mostly rejected because close does not reclaim arbitrary firmware objects. Tests should cover UID allocation failure, UID release on unregister with open fds, each allowed scope tier, ACCESS_REG read versus write `op_mod`, output buffer reuse, `-EREMOTEIO` response propagation, and denied object-creating commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/mlx5/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/pds/Makefile -->
# sources/distributed-fs/ceph-client/drivers/fwctl/pds/Makefile

## Purpose
This Kbuild file builds the AMD/Pensando PDS fwctl provider.

## Important Entries
`obj-$(CONFIG_FWCTL_PDS) += pds_fwctl.o` and `pds_fwctl-y += main.o` map the Kconfig symbol to the provider implementation.

## Control Flow and State
No runtime behavior or state is defined in this Makefile.

## Dependencies and Integration Points
The provider object depends on the PDS core auxiliary bus infrastructure and fwctl namespace exports.

## Risks and Test Signals
Build test the object with PDS core enabled as module and built-in, and confirm Kconfig dependency prevents unresolved PDS symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/pds/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/pds/main.c -->
# sources/distributed-fs/ceph-client/drivers/fwctl/pds/main.c

## Purpose
`pds/main.c` is the AMD/Pensando DSC fwctl provider. It discovers firmware RPC endpoints and operations through PDS admin queue commands, validates userspace RPCs against firmware-advertised limits and operation scopes, and submits indirect request and response payloads through DMA-mapped buffers.

## Important APIs, Types, and Functions
Key state is `struct pdsfc_dev`, which embeds `struct fwctl_device`, stores the PDS auxiliary device, caps, identify data, a coherent endpoint query page, and per-endpoint cached operation pages. `struct pdsfc_rpc_endpoint_info` stores endpoint id, operations DMA page, and a mutex. fwctl callbacks are `pdsfc_open_uctx()`, `pdsfc_close_uctx()`, `pdsfc_info()`, and `pdsfc_fw_rpc()`. Discovery and validation helpers include `pdsfc_identify()`, `pdsfc_get_endpoints()`, `pdsfc_init_endpoints()`, `pdsfc_get_operations()`, and `pdsfc_validate_rpc()`.

## Control Flow
Probe allocates the fwctl device, sends `PDS_FWCTL_CMD_IDENT` into a coherent identify buffer, queries root endpoints into a page-sized coherent buffer, allocates per-endpoint cache records, sets query/send caps, and registers fwctl. Open copies device caps into the user context. Validation rejects request or response lengths above firmware max sizes, checks that the endpoint exists, lazily queries and caches that endpoint's operation list under its mutex, translates firmware command attributes into fwctl scopes, and rejects unsupported or insufficient-scope operations.

RPC copies the input payload from a userspace pointer inside `struct fwctl_rpc_pds`, maps input for DMA to device, allocates and maps output for DMA from device, sends `PDS_FWCTL_CMD_RPC` with indirect request and response flags, copies output payload back to userspace, stores firmware retval from the completion, and returns the original RPC struct as output. Remove unregisters fwctl, frees cached operation pages, frees endpoints, and drops the fwctl object.

## State and Persistence
State is in memory and coherent DMA pages. Endpoint lists persist for device lifetime; operation lists are lazily cached per endpoint. There is no disk persistence. Per-endpoint mutexes serialize lazy query and cache installation.

## Dependencies and Integration Points
The driver depends on PDS admin queue APIs, PDS core interface definitions, auxiliary bus, DMA mapping, fwctl uapi, and `uapi/fwctl/pds.h`.

## Risks and Test Signals
`pdsfc_info()` allocates `struct fwctl_info_pds` and fills caps but does not assign `*length`, unlike the BNXT and mlx5 providers; the core may report zero provider-info length. In `pdsfc_validate_rpc()`, a failed operation query returns `-ENOMEM` for any `ERR_PTR`, losing the real error. DMA mapping cleanup is careful but should be tested for every allocation and mapping failure. Tests should cover identify failure, endpoint query failure, lazy operations caching under concurrent RPCs, all scope translations, max request/response limits, zero-length payloads, firmware completion retval propagation, remove after cached operations exist, and info length reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fwctl/pds/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gnss/Kconfig

## Purpose
This Kconfig file defines the Linux GNSS receiver subsystem and transport or chipset drivers for serial and USB GNSS devices.

## Important Entries
`GNSS` builds the core `gnss` module. `GNSS_SERIAL` is a hidden helper selected by `GNSS_MTK_SERIAL` and `GNSS_UBX_SERIAL`. Concrete drivers are `GNSS_MTK_SERIAL`, `GNSS_SIRF_SERIAL`, `GNSS_UBX_SERIAL`, and `GNSS_USB`, with dependencies on `SERIAL_DEV_BUS` or `USB`.

## Control Flow and State
There is no runtime control flow. Kconfig controls whether the GNSS char-device core and transport drivers are compiled.

## Dependencies and Integration Points
The serial drivers integrate with serdev and device-tree compatible strings. USB support integrates with the USB core.

## Risks and Test Signals
The SiRF driver depends directly on `SERIAL_DEV_BUS` but does not select `GNSS_SERIAL` because it implements its own serial handling. Configuration tests should build each driver alone and in combinations, including module and built-in variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gnss/Makefile

## Purpose
This Makefile maps GNSS Kconfig symbols to core and driver objects.

## Important Entries
`gnss-y := core.o` builds the core. `gnss-serial-y := serial.o`, `gnss-mtk-y := mtk.o`, `gnss-sirf-y := sirf.o`, `gnss-ubx-y := ubx.o`, and `gnss-usb-y := usb.o` build the helper and concrete modules.

## Control Flow and State
There is no runtime state. Kbuild selects objects based on configuration.

## Dependencies and Integration Points
The build outputs correspond to the exported symbols in core and serial helper code.

## Risks and Test Signals
Build tests should verify that serial helper symbols resolve for MTK and UBX and that SiRF has no unnecessary dependency on `gnss-serial.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/core.c -->
# sources/distributed-fs/ceph-client/drivers/gnss/core.c

## Purpose
`core.c` implements the GNSS character-device subsystem. It allocates `/dev/gnssN` devices, buffers incoming raw receiver data in a FIFO, provides blocking read and synchronous write operations, exposes receiver type through sysfs and uevents, and manages disconnect/open lifetimes for transport drivers.

## Important APIs, Types, and Functions
Public exported APIs are `gnss_allocate_device()`, `gnss_put_device()`, `gnss_register_device()`, `gnss_deregister_device()`, and `gnss_insert_raw()`. File operations are `gnss_open()`, `gnss_release()`, `gnss_read()`, `gnss_write()`, and `gnss_poll()`. Internal constants are `GNSS_MINORS`, `GNSS_READ_FIFO_SIZE`, and `GNSS_WRITE_BUF_SIZE`.

## Control Flow
Module init allocates 16 char minors and creates class `gnss`. Transport drivers allocate a `struct gnss_device`, set type and operations, then register it. Open takes a device reference, checks `disconnected` under `rwsem`, increments the open count, and calls transport `open()` on the first opener. Release decrements count and calls transport `close()` on the last close, resetting the read FIFO.

Reads block until data is available, the device disconnects, or a signal arrives. Incoming bytes are inserted by transport callbacks through `gnss_insert_raw()`, which wakes the read queue. Writes require a transport `write_raw` operation, copy userspace data in 1024-byte chunks under `write_mutex`, and call the transport while holding the read side of `rwsem`. Deregistration marks the device disconnected, wakes readers, closes active hardware once, and deletes the cdev.

## State and Persistence
State is volatile: IDA minor allocation, open count, disconnected flag, kfifo contents, write staging buffer, mutexes, rwsem, and wait queue. No GNSS data or configuration is persisted.

## Dependencies and Integration Points
The core depends on cdev, class, kfifo, IDA, wait queues, poll, and `linux/gnss.h`. Serial and USB drivers use the exported APIs.

## Risks and Test Signals
`gnss_insert_raw()` assumes caller serialization and must not be called for a closed device; transport drivers must honor that contract. FIFO overflow silently drops data by returning fewer bytes inserted. Writes ignore `O_NONBLOCK` by design and assume transport write can accept 1024-byte chunks. Tests should cover open count transitions, blocking read wakeup, disconnect read returning EOF, poll `EPOLLHUP`, write chunking, FIFO overflow accounting, and transport open failure rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/mtk.c -->
# sources/distributed-fs/ceph-client/drivers/gnss/mtk.c

## Purpose
`mtk.c` is the Mediatek serial GNSS receiver driver. It uses the generic GNSS serial helper and supplies regulator-based power control for Mediatek-compatible modules.

## Important APIs, Types, and Functions
Private state is `struct mtk_data` with `vcc` and optional `vbackup` regulators. Power callbacks are `mtk_set_active()`, `mtk_set_standby()`, and `mtk_set_power()`, installed through `struct gnss_serial_ops`. Probe and remove are `mtk_probe()` and `mtk_remove()`.

## Control Flow
Probe allocates a generic serial GNSS device with room for `mtk_data`, sets GNSS type `GNSS_TYPE_MTK`, gets mandatory `vcc` and optional `vbackup`, enables backup power if present, and registers the serial GNSS device. The generic serial helper handles serdev open, baud rate, runtime PM, read insertion, and write_raw. Remove deregisters, disables backup power, and frees the serial wrapper.

## State and Persistence
Runtime state is the regulator handles and GNSS serial object. Backup regulator state persists only while the driver is bound. There is no stored configuration.

## Dependencies and Integration Points
The driver depends on serdev, regulator framework, GNSS serial helper, and OF compatible `globaltop,pa6h`.

## Risks and Test Signals
Power sequencing is minimal: `vcc` is toggled for active/standby and `vbackup` remains enabled for bind lifetime. Tests should cover missing optional backup regulator, regulator enable failure, runtime suspend/resume through `gnss_serial_pm_ops`, registration failure cleanup, and serial read/write through the generic helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/mtk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/serial.c -->
# sources/distributed-fs/ceph-client/drivers/gnss/serial.c

## Purpose
`serial.c` is a reusable helper for GNSS receivers attached through the serdev bus. It adapts serdev open, receive, transmit, baud-rate setup, and power management into the GNSS core operations used by simple serial GNSS chipset drivers.

## Important APIs, Types, and Functions
Exported functions are `gnss_serial_allocate()`, `gnss_serial_free()`, `gnss_serial_register()`, and `gnss_serial_deregister()`. GNSS ops are `gnss_serial_open()`, `gnss_serial_close()`, and `gnss_serial_write_raw()`. Serdev callbacks are `gnss_serial_receive_buf()` and `serdev_device_write_wakeup`. Power integration is through `gnss_serial_set_power()` and exported `gnss_serial_pm_ops`.

## Control Flow
Allocation creates `struct gnss_serial` plus caller private storage, allocates a GNSS core device, installs generic GNSS operations, sets serdev driver data and client ops, and parses `current-speed` from device tree with a default of 4800 baud. Register enables runtime PM when configured, or directly powers the device active otherwise, then registers the GNSS cdev. Open opens the serdev port, configures baud and no flow control, then runtime-resumes the device. Receive callbacks insert raw bytes into the GNSS FIFO. Write uses synchronous `serdev_device_write()` and waits until sent.

## State and Persistence
State includes the serdev pointer, GNSS device pointer, configured speed, optional chipset power ops, and flexible private driver data. No configuration is persisted outside device tree properties.

## Dependencies and Integration Points
The helper depends on GNSS core APIs, serdev, runtime PM, OF property parsing, and chipset drivers such as MTK and UBX.

## Risks and Test Signals
The write path treats short positive writes as its return value, which the GNSS core will use for progress; repeated short writes may need coverage. Runtime PM errors during open close the serdev and roll back. Tests should cover default and DT baud rate, runtime PM disabled builds, receive FIFO overflow propagation, write interruption/short write, register failure cleanup, and suspend/resume behavior when runtime-suspended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/serial.h -->
# sources/distributed-fs/ceph-client/drivers/gnss/serial.h

## Purpose
`serial.h` declares the private GNSS serial helper interface used by serial chipset drivers.

## Important APIs, Types, and Functions
`struct gnss_serial` stores the serdev device, GNSS core device, baud speed, optional `struct gnss_serial_ops`, and flexible driver data. `enum gnss_serial_pm_state` defines `OFF`, `ACTIVE`, and `STANDBY`. `struct gnss_serial_ops` currently exposes `set_power()`. The header declares allocation, free, register, deregister, exported PM ops, and `gnss_serial_get_drvdata()`.

## Control Flow and State
The header has no runtime flow. It defines how chipset drivers attach their private state to the generic serial helper and provide power transitions.

## Dependencies and Integration Points
It depends on termbits for `speed_t`, PM types, and opaque GNSS/serdev types supplied by includers. MTK and UBX use it directly.

## Risks and Test Signals
The flexible array driver data requires callers to request enough private bytes during allocation. Compile tests should catch prototype drift between header and implementation. Runtime tests should verify power callback ordering across register, open, close, suspend, and deregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/serial.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/sirf.c -->
# sources/distributed-fs/ceph-client/drivers/gnss/sirf.c

## Purpose
`sirf.c` is the SiRFstar serial GNSS driver. Unlike MTK and UBX, it implements its own serdev and power state machine to handle SiRF on/off pulse GPIOs, optional wakeup GPIO interrupts, regulators, and active/hibernate detection.

## Important APIs, Types, and Functions
`struct sirf_data` stores the GNSS device, serdev, speed, `vcc` and `lna` regulators, optional `on_off` and `wakeup` GPIOs, IRQ, active/open flags, serdev open count, mutexes, and wait queue. Important helpers are `sirf_serdev_open()`, `sirf_serdev_close()`, `sirf_open()`, `sirf_close()`, `sirf_receive_buf()`, `sirf_wait_for_power_state()`, `sirf_set_active()`, `sirf_runtime_suspend()`, and `sirf_runtime_resume()`.

## Control Flow
Probe allocates a GNSS device, initializes mutexes and wait queue, installs serdev callbacks, reads `current-speed` with default 9600 baud, gets mandatory regulators, and optionally gets `sirf,onoff` and `sirf,wakeup` GPIOs. With an on/off GPIO, it enables `vcc`, waits for boot into hibernate, samples or infers active state, requests a threaded wakeup IRQ if available, and forces hibernate if already active. Runtime PM is then enabled or, without PM, the device is powered active before GNSS registration.

Open marks the GNSS file open, opens serdev through a reference-counted helper, and runtime-resumes the device. Receive callbacks update active state when no wakeup GPIO is available and insert data only while the GNSS file is open. Suspend powers down by pulsing on/off or disabling `vcc`, then disables `lna`; resume reverses that sequence. Remove deregisters GNSS, disables PM or suspends, frees IRQ, disables always-on `vcc` for on/off boards, and drops the GNSS device.

## State and Persistence
State is volatile but richer than the generic serial helper: active state can be IRQ-driven or inferred from received data, serdev open is reference-counted separately from GNSS open, and power waits use a wait queue. No settings are persisted.

## Dependencies and Integration Points
The driver depends on GNSS core, serdev, regulator, GPIO descriptor, threaded IRQ, runtime PM, and OF compatibles for Fastrax, Linx, and Wi2Wi modules.

## Risks and Test Signals
When no wakeup GPIO exists, active/hibernate detection depends on receiving data within `SIRF_REPORT_CYCLE`, which comments call unreliable for long report intervals or motion-triggered output. Power failure rollback re-enables prior regulators and logs secondary failures. Tests should cover wakeup and no-wakeup boards, pulse retries, runtime and system suspend/resume, regulator failure rollback, open failure cleanup, receive while closed, and removal with the device open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/sirf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/ubx.c -->
# sources/distributed-fs/ceph-client/drivers/gnss/ubx.c

## Purpose
`ubx.c` is the u-blox serial GNSS receiver driver. It uses the generic GNSS serial helper and adds regulator and GPIO setup for common u-blox modules.

## Important APIs, Types, and Functions
Private state is `struct ubx_data` containing the `vcc` regulator. Power callbacks are `ubx_set_active()`, `ubx_set_standby()`, and `ubx_set_power()`. Probe and remove are `ubx_probe()` and `ubx_remove()`.

## Control Flow
Probe allocates a serial GNSS wrapper, sets power ops and type `GNSS_TYPE_UBX`, gets mandatory `vcc`, optionally enables backup regulator `v-bckp`, deasserts optional `safeboot` and `reset` GPIOs by driving them low, and registers the serial GNSS device. The serial helper handles serdev open/close, data flow, and PM. Remove deregisters and frees the wrapper.

## State and Persistence
Runtime state is the serial wrapper, GNSS device, regulator handle, and devm-managed GPIO/regulator resources. There is no persistent state.

## Dependencies and Integration Points
The driver depends on serdev, GNSS serial helper, regulator and GPIO descriptor frameworks, and OF compatibles `u-blox,neo-6m`, `u-blox,neo-8`, and `u-blox,neo-m8`.

## Risks and Test Signals
Backup regulator is enabled by devm helper and not explicitly disabled in remove, relying on devm cleanup. Safeboot and reset GPIO polarity depends on board descriptions matching `GPIOD_OUT_LOW`. Tests should cover optional resource absence, mandatory `vcc` failure, GPIO acquisition failure, PM transitions, and GNSS read/write through serdev.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/ubx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/usb.c -->
# sources/distributed-fs/ceph-client/drivers/gnss/usb.c

## Purpose
`usb.c` is a generic USB GNSS receiver driver. It exposes USB bulk GNSS devices as GNSS core character devices with continuous bulk-in URB reception and synchronous bulk-out writes.

## Important APIs, Types, and Functions
Private state is `struct gnss_usb`, storing the USB device, interface, GNSS device, read URB, and write pipe. GNSS ops are `gnss_usb_open()`, `gnss_usb_close()`, and `gnss_usb_write_raw()`. USB callbacks are `gnss_usb_probe()`, `gnss_usb_disconnect()`, and `gnss_usb_rx_complete()`.

## Control Flow
Probe finds one bulk-in and one bulk-out endpoint, allocates private state and a GNSS device, sets type `GNSS_TYPE_NMEA`, allocates a bulk read URB and buffer sized to at least 512 bytes, fills the URB, registers the GNSS device, and stores interface data. Open submits the read URB; completion inserts received bytes into the GNSS FIFO and resubmits unless the URB was stopped or shut down. Write duplicates the caller buffer and sends it with `usb_bulk_msg()` and a 1000 ms timeout. Disconnect deregisters GNSS, frees the URB buffer and URB, drops the GNSS device, and frees private state.

## State and Persistence
State is in memory only: USB pointers, one reusable read URB, write pipe, and GNSS FIFO state in the core. There is no persistent configuration.

## Dependencies and Integration Points
The driver depends on USB core APIs and GNSS core APIs. The current ID table matches Sierra Wireless XM1210 (`1199:b000`).

## Risks and Test Signals
The receive path drops bytes when the GNSS FIFO is full and only logs debug. Write allocates a temporary buffer for every call. The driver relies on GNSS deregistration closing/killing the URB before freeing it. Tests should cover endpoint discovery failure, open/close URB submit and kill, disconnect while open, receive resubmit after transient URB errors, FIFO overflow, write timeout, and short or failed bulk writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gnss/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpib/Kconfig

## Purpose
This Kconfig file defines a set of Linux GPIB adapter drivers and hidden helper modules for the GPIB subsystem.

## Important Entries
Top-level `GPIB` enables the menu. `GPIB_COMMON` provides the core userspace interface. Board drivers include Agilent 82350B PCI, Agilent 82357A USB, CEC PCI, NI PCI/ISA/TNT, CB7210, NI USB, Fluke, FMH, GPIO bitbang, HP82335, HP82341, INES, LPVO, and PC2. Hidden helpers include `GPIB_TMS9914`, `GPIB_NEC7210`, and `GPIB_PCMCIA`.

## Control Flow and State
There is no runtime flow. Kconfig dependencies select common bus, IO port, PCI, USB, OF, ISA, and PCMCIA support as needed.

## Dependencies and Integration Points
Most board drivers select `GPIB_COMMON` plus a chip helper such as `GPIB_NEC7210` or `GPIB_TMS9914`. Userspace integration is through the linux-gpib library mentioned in help text.

## Risks and Test Signals
The help text has rough edges, including a `called cb7210` line appearing under the INES entry after the CB7210 entry, which can confuse menu help. The `depends on PCMCIA || !PCMCIA` pattern is used to force visibility across PCMCIA states. Test signals are Kconfig lint, allmodconfig, and per-driver dependency builds on platforms with and without IO ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/Makefile

## Purpose
This Makefile routes GPIB Kconfig symbols to board and helper subdirectories and adds the common include path.

## Important Entries
`subdir-ccflags-y += -I$(src)/include` exposes shared GPIB headers. Each board or helper symbol adds its subdirectory, including Agilent, CB7210, CEC, common, NEC7210, TMS9914, and TNT4882 families.

## Control Flow and State
There is no runtime state. Kbuild evaluates `obj-$(CONFIG_...)` entries to descend into selected subdirectories.

## Dependencies and Integration Points
This file integrates the staging-style GPIB tree with Kbuild and shared headers under `drivers/gpib/include`.

## Risks and Test Signals
Missing subdir entries would silently omit modules even when Kconfig is enabled. Build tests should cover each selected subdirectory and confirm include path availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/agilent_82350b/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/agilent_82350b/Makefile

## Purpose
This Kbuild file builds the Agilent 82350B family GPIB PCI driver.

## Important Entries
`obj-$(CONFIG_GPIB_AGILENT_82350B) += agilent_82350b.o` maps the Kconfig symbol to the module object.

## Control Flow and State
No runtime behavior is defined here.

## Dependencies and Integration Points
The object depends on the GPIB common core and TMS9914 helper selected by Kconfig.

## Risks and Test Signals
Test modular builds with `GPIB_AGILENT_82350B=m` and ensure helper symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/agilent_82350b/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/agilent_82350b/agilent_82350b.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/agilent_82350b/agilent_82350b.c

## Purpose
`agilent_82350b.c` implements GPIB support for HP/Agilent/Keysight 82350A, 82350B, and 82351A PCI or PCIe adapters. It wraps TMS9914 core operations and optionally accelerates transfers through board SRAM/FIFO streaming.

## Important APIs, Types, and Functions
Private state is `struct agilent_82350b_priv` from the companion header. Accelerated paths are `agilent_82350b_accel_read()` and `agilent_82350b_accel_write()`. Wrapper operations delegate to TMS9914 helpers for command, control, addressing, EOS, polling, status, and local/remote operations. Hardware setup is in `agilent_82350b_generic_attach()`, `init_82350a_hardware()`, `test_sram()`, and `agilent_82350b_detach()`. IRQ handling is `agilent_82350b_interrupt()`.

## Control Flow
Module init registers a PCI ID table for discovery and two GPIB interfaces: accelerated `agilent_82350b` and unaccelerated `agilent_82350b_unaccel`. The PCI probe is a stub; actual board selection happens in GPIB `attach()` using `gpib_pci_get_device()` or subsystem matching. Attach enables PCI, requests BAR regions, maps model-specific registers, loads 82350A firmware from `config->init_data` when required, tests SRAM, requests IRQ, enables PCI and TMS9914 interrupts, configures FIFO events if requested, sets T1 delay, resets the TMS9914, and brings the board online.

Accelerated reads disable FIFO briefly, handle a first-byte holdoff corner case, stream blocks through SRAM until transfer count or buffer-end events, then fall back to TMS9914 for final bytes. Accelerated writes send the first byte through the TMS9914, stream even FIFO blocks from host SRAM, and use TMS9914 for final EOI byte. The IRQ reads board event status, dispatches TMS9914 status when present, write-clears FIFO event bits, records them in private state under the board spinlock, and wakes waiters.

## State and Persistence
Runtime state includes mapped register bases, PCI device reference, IRQ number, card mode bits, latched event bits, model, FIFO mode, and TMS9914 private state. There is no persistence except optional firmware passed during attach for 82350A initialization.

## Dependencies and Integration Points
The driver depends on PCI, MMIO accessors, GPIB core registration, PLX9050 registers for 82350A, and the TMS9914 helper.

## Risks and Test Signals
Several attach error paths return without calling detach, so mapped resources or PCI regions can leak after mid-attach failures. The PCI driver exists mainly for ID exposure and has no real binding in probe. Accelerated paths manipulate TMS9914 interrupt masks and holdoff state, so they need race testing with timeouts and device clear. Tests should cover each board model, missing 82350A firmware, SRAM test failure, FIFO and non-FIFO transfers, EOI/EOS behavior, IRQ event wakeups, detach after partial attach, and shared IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/agilent_82350b/agilent_82350b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/agilent_82350b/agilent_82350b.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/agilent_82350b/agilent_82350b.h

## Purpose
`agilent_82350b.h` defines register maps, PCI identifiers, model enums, bit fields, and private state for the Agilent 82350B-family GPIB driver.

## Important APIs, Types, and Functions
The header defines vendor/device IDs for Agilent and 82350/82351 hardware, BAR index enums for 82350A and 82350B layouts, `enum board_model`, and `struct agilent_82350b_priv`. Register enums cover card mode, interrupt/event, stream status, transfer counter, TMS9914 base, and SRAM access control. Bit enums describe card mode, interrupt enable, event status, internal config, SRAM direction/FIFO enable, and 82350A BORG firmware loader status. `agilent_82350b_fifo_is_halted()` reads stream halt state.

## Control Flow and State Model
The header does not execute code beyond the inline status read. It defines how the C file maps hardware BARs and how FIFO/SRAM streaming is controlled.

## Dependencies and Integration Points
It depends on shared GPIB, PLX9050, and TMS9914 headers. Its structures are private to the Agilent driver.

## Risks and Test Signals
Register offsets and BAR indexes are hardware ABI. Mistakes here affect every transfer path. Tests should verify model detection maps correct BARs, event bits are write-cleared as expected, transfer counter complement math matches hardware, and the FIFO halt bit transitions during streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/agilent_82350b/agilent_82350b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/agilent_82357a/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/agilent_82357a/Makefile

## Purpose
This Kbuild file builds the Agilent 82357A/B USB GPIB driver.

## Important Entries
`obj-$(CONFIG_GPIB_AGILENT_82357A) += agilent_82357a.o` maps the Kconfig symbol to the module object.

## Control Flow and State
No runtime behavior is defined here.

## Dependencies and Integration Points
The object depends on USB and the GPIB common core selected by Kconfig.

## Risks and Test Signals
Build tests should verify USB and GPIB symbols resolve for modular and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/agilent_82357a/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/agilent_82357a/agilent_82357a.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/agilent_82357a/agilent_82357a.c

## Purpose
`agilent_82357a.c` implements the Agilent/Keysight 82357A and 82357B USB-to-GPIB adapters. It bridges the linux-gpib interface to vendor USB bulk, interrupt, and control messages and manages hotplug independently from GPIB board attach.

## Important APIs, Types, and Functions
Private state is `struct agilent_82357a_priv`, defined in the header. USB transfer helpers are `agilent_82357a_send_bulk_msg()`, `agilent_82357a_receive_bulk_msg()`, `agilent_82357a_receive_control_msg()`, `agilent_82357a_write_registers()`, `agilent_82357a_read_registers()`, and `agilent_82357a_abort()`. GPIB data paths are `agilent_82357a_read()`, `agilent_82357a_generic_write()`, `agilent_82357a_write()`, and `agilent_82357a_command()`. Setup and lifecycle functions include `agilent_82357a_setup_urbs()`, `agilent_82357a_init()`, `agilent_82357a_attach()`, `agilent_82357a_detach()`, USB probe/disconnect/suspend/resume, and module init/exit.

## Control Flow
Module init registers a USB driver and one GPIB interface. USB probe only records an available interface in a global table protected by `agilent_82357a_hotplug_lock`; GPIB attach later selects an unclaimed interface by optional device path or serial number, sets endpoints according to product ID, starts the interrupt URB, initializes firmware registers, and marks the board attached. Disconnect clears the global table entry, kills active URBs, and nulls `bus_interface` under allocation locks so later operations return `-ENODEV`.

Bulk helper functions allocate one URB at a time, serialize allocation and protocol transfers with mutexes, use a timer to complete timed-out URBs, and kill/free URBs on cleanup. Writes send a protocol header plus payload, wait for a write-complete interrupt or board timeout, then read a vendor control status block for byte count. Reads send a read command, receive payload plus trailing flags, abort and drain on timeout, set END on EOI/EOS flags, and force ATN to refresh status. Register reads and writes are short bulk protocols with response validation. Suspend aborts transfers, idles firmware, and kills URBs; resume restarts the interrupt URB, reinitializes firmware, restores system-controller and REN state, and toggles IFC when master.

## State and Persistence
State includes a global array of up to 128 USB interfaces, per-board mutexes, bulk and interrupt URBs, timer/completion context, endpoint numbers, EOS settings, hardware control bits, interrupt flags, CIC and REN state. There is no disk persistence.

## Dependencies and Integration Points
The driver depends on USB core, GPIB common core, TMS9914 register definitions, wait queues, timers, completions, and userspace board configuration matching by path or serial.

## Risks and Test Signals
Some error paths in register helpers return without freeing `in_data` after response validation failures. Detach locks allocation mutexes and then frees private state without unlocking them, which is safe only because the object is destroyed but is unusual and should be reviewed with lockdep expectations. Global interface matching allows hotplug and attach to be decoupled but limits devices to 128 and requires careful disconnect races. Tests should cover A and B endpoint selection, attach before firmware-loaded IDs are present, serial/path matching, read timeout abort and drain, write no-listener detection, interrupt URB resubmit, suspend/resume restoration, disconnect during blocked transfer, and module unload with attached boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/agilent_82357a/agilent_82357a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/agilent_82357a/agilent_82357a.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/agilent_82357a/agilent_82357a.h

## Purpose
`agilent_82357a.h` defines the USB protocol constants, firmware registers, transfer flags, error codes, endpoint addresses, and private state for the 82357A/B USB GPIB driver.

## Important APIs, Types, and Functions
The header defines Agilent USB vendor/product IDs, pre-firmware IDs, endpoint addresses for A and B variants, bulk command opcodes, read/write/trailing flags, interrupt flag bit numbers, vendor error codes, control values for transfer abort/status, and firmware registers. `struct agilent_82357a_priv` stores USB interface, EOS settings, hardware control bits, interrupt flags, URBs, buffers, mutexes, timer, completion context, endpoints, and CIC/REN state. `struct agilent_82357a_register_pairlet` describes register transactions.

## Control Flow and State Model
The header itself has no runtime flow. It defines the protocol format consumed by `agilent_82357a.c`.

## Dependencies and Integration Points
It depends on USB, mutex, completion, timer, GPIB common, and TMS9914 headers. The definitions are private to the driver.

## Risks and Test Signals
The endpoint constants differ between 82357A and 82357B, so product selection must be exact. Transfer flag semantics drive END, ATN, abort, and count behavior. Tests should validate protocol packets against hardware traces or documentation and cover error-code translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/agilent_82357a/agilent_82357a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/cb7210/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/cb7210/Makefile

## Purpose
This Kbuild file builds the Measurement Computing/CB7210 GPIB driver.

## Important Entries
`obj-$(CONFIG_GPIB_CB7210) += cb7210.o` maps the Kconfig symbol to the module object.

## Control Flow and State
No runtime behavior is defined in this file.

## Dependencies and Integration Points
The object depends on GPIB common and NEC7210 helpers selected by Kconfig.

## Risks and Test Signals
Build tests should cover PCI/ISA and optional PCMCIA configurations so conditional code compiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/cb7210/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/cb7210/cb7210.c -->
# sources/distributed-fs/ceph-client/drivers/gpib/cb7210/cb7210.c

## Purpose
`cb7210.c` implements Measurement Computing/ComputerBoards CB7210.2 and CBI488.2 based GPIB adapters across PCI, ISA, and optional PCMCIA variants. It wraps NEC7210 core operations and adds high-speed FIFO acceleration.

## Important APIs, Types, and Functions
Private state is `struct cb7210_priv` from the header. FIFO paths are `input_fifo_enable()`, `fifo_read()`, `cb7210_accel_read()`, `output_fifo_enable()`, `fifo_write()`, and `cb7210_accel_write()`. Interrupt handling is split across `cb_pci_interrupt()`, `cb7210_internal_interrupt()`, `cb7210_locked_internal_interrupt()`, and `cb7210_interrupt()`. Attach/detach paths are `cb_pci_attach()`, `cb_pci_detach()`, `cb_isa_attach()`, `cb_isa_detach()`, plus PCMCIA variants under `CONFIG_GPIB_PCMCIA`.

## Control Flow
Module init registers a stub PCI driver and multiple GPIB interface names for PCI, ISA, accelerated, and unaccelerated modes, plus PCMCIA interfaces if enabled. Generic attach allocates private state, initializes NEC7210 private data, and sets IO-port access methods. PCI attach discovers supported ComputerBoards or Quancom PCI devices through helper lookup, enables PCI, requests regions, records IO bases, requests shared IRQ, enables AMCC mailbox interrupts where needed, and calls `cb7210_init()`. ISA attach requests configured IO ports and IRQ. PCMCIA probe configures the socket and stores a global current device; GPIB attach then claims its IO/IRQ resources.

`cb7210_init()` resets the CB7210 high-speed logic, configures IRQ level bits, resets and onlines the NEC7210, handles Quancom interrupt polarity, and requests a pseudo IRQ for polling. Accelerated reads prime one byte through NEC7210 holdoff, stream FIFO words while waiting for half-full or END conditions, then read a final byte through NEC7210. Accelerated writes send all even-sized bulk data through the FIFO and use NEC7210 for the leftover byte and optional EOI. Interrupts clear high-speed FIFO, SRQ, and EOI status bits and wake the GPIB wait queue.

## State and Persistence
Runtime state includes PCI or ISA resources, IO bases, IRQ number, selected PCI chip, high-speed mode bits, FIFO half-empty/full flags, and NEC7210 state. PCMCIA uses a single global `curr_dev`. No persistent storage exists.

## Dependencies and Integration Points
The driver depends on GPIB core registration, NEC7210 helper APIs, AMCC S5933 and Quancom PCI definitions, PCI/ISA IO ports, IRQs, pseudo IRQ support, and optional PCMCIA services.

## Risks and Test Signals
Several attach error paths allocate private data or request resources and then return without generic detach cleanup. `cb_pci_detach()` unconditionally writes AMCC interrupt control when `irq` is set, even for Quancom devices where `amcc_iobase` is not valid, which deserves review. PCMCIA support tracks only one `curr_dev`, limiting multiple-card behavior. Tests should cover PCI AMCC and Quancom boards, ISA IRQ validation, FIFO read/write boundary and odd-length behavior, END/EOI handling, pseudo IRQ polling, detach after partial attach failures, PCMCIA insert/remove, and interrupt races around high-speed mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/cb7210/cb7210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/cb7210/cb7210.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/cb7210/cb7210.h

## Purpose
`cb7210.h` defines private state, register helpers, PCI IDs, FIFO constants, and CB7210/CBI488.2 high-speed mode bits for the CB7210 GPIB driver.

## Important APIs, Types, and Functions
`struct cb7210_priv` embeds `struct nec7210_priv`, stores PCI device, AMCC and FIFO IO bases, IRQ, PCI chip type, high-speed mode bits, and FIFO event flags. Inline helpers include `nec7210_iobase()`, `cb7210_page_in_bits()`, paged read/write helpers, direct high-speed register read/write helpers, and `irq_bits()`. Enums define bus status bits, high-speed mode/status/interrupt-level bits, and CB7210 AUX commands including `AUX_RTL2`, `AUX_LO_SPEED`, and `AUX_HI_SPEED`.

## Control Flow and State Model
The header wraps IO port access and protects paged NEC7210 registers with the NEC register page lock. It defines the state bits used by interrupt and FIFO paths in `cb7210.c`.

## Dependencies and Integration Points
It depends on NEC7210, GPIB common, AMCC S5933, delay, and interrupt headers. It also defines local PCI IDs for supported ComputerBoards devices.

## Risks and Test Signals
The direct high-speed register helpers are documented as unsafe for registers below 8 because they do not lock. `irq_bits()` accepts only specific legacy IRQs; invalid IRQs return zero, which can also represent IRQ 0 bits and must be interpreted carefully. Tests should validate paged register locking, high-speed status bit interpretation, IRQ programming, and FIFO IO base assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/cb7210/cb7210.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/cec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpib/cec/Makefile

## Purpose
This Kbuild file builds the CEC PCI GPIB driver.

## Important Entries
`obj-$(CONFIG_GPIB_CEC_PCI) += cec_gpib.o` maps the Kconfig symbol to the implementation object.

## Control Flow and State
No runtime behavior is defined here.

## Dependencies and Integration Points
The object depends on GPIB common and NEC7210 helpers selected by Kconfig.

## Risks and Test Signals
Build tests should cover `GPIB_CEC_PCI=m` with PCI, IO port, and NEC7210 support enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/cec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/cec/cec.h -->
# sources/distributed-fs/ceph-client/drivers/gpib/cec/cec.h

## Purpose
`cec.h` defines the private data and register spacing for the Capital Equipment Corporation PCI-488 and Keithley KPCI-488 GPIB driver.

## Important APIs, Types, and Functions
`struct cec_priv` embeds `struct nec7210_priv`, stores the PCI device pointer, PLX9052 IO base, and IRQ number. `cec_reg_offset` is a constant register stride of 1 between NEC7210 registers.

## Control Flow and State Model
The header contains no runtime flow. It supplies the state layout used by the CEC implementation.

## Dependencies and Integration Points
It depends on NEC7210, GPIB common, and PLX9050 register definitions. The implementation uses these fields to map the PLX bridge and NEC7210 core.

## Risks and Test Signals
The private structure assumes a PLX-backed PCI design and NEC7210-compatible register spacing. Tests should cover resource setup, IRQ disable/free on detach, and correct register-offset use against actual CEC/KPCI hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpib/cec/cec.h -->
