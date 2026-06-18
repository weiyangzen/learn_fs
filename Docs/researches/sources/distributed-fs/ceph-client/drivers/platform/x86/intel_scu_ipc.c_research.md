<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_ipc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_ipc.c

Purpose: core driver and exported API for Intel SCU IPC-1 communication. It registers a single SCU IPC device, serializes commands to SCU firmware through MMIO command/status/data registers, and exposes helper calls for PMIC/MSIC register access and generic SCU commands.

Important APIs/types/functions: `struct intel_scu_ipc_dev` wraps a `struct device`, owner module, MMIO base, completion, and platform data. Public get/put APIs manage references and module lifetime. `pwr_reg_rdwr()` implements power-controller read/write/update commands. Exported helpers include `intel_scu_ipc_dev_ioread8()`, `iowrite8()`, `readv()`, `writev()`, `update()`, `simple_command()`, and `command_with_size()`. Registration APIs `__intel_scu_ipc_register()` and `__devm_intel_scu_ipc_register()` create the provider device.

Control flow: subsystem init registers the `intel_scu_ipc` class. A PCI or platform provider calls register with memory and optional IRQ resources. The core reserves and maps MMIO, optionally requests IRQ, registers a device, and stores the singleton `ipcdev`. Command helpers acquire `ipclock`, check for busy status, write input data, issue an IPC command with IOC bit, then wait either for completion interrupt or polling. Results are copied from read buffers and errors are converted to `-EIO`, `-EBUSY`, or `-ETIMEDOUT`.

State/persistence: singleton `ipcdev` and `ipclock` serialize all access. Hardware SCU state persists outside the driver. Device references and module owner pins prevent provider unload while consumers hold the IPC device. Release frees IRQ, unmaps MMIO, releases memory region, and frees the object.

Dependencies/integration: depends on platform data type `intel_scu_ipc_data`, Linux device/class model, completions, MMIO, interrupts, and exported symbols used by other Intel MID/SCU platform drivers. PCI and ACPI platform instantiators feed resources into this core.

Risks: only one IPC instance is supported. Buffer sizes are small hardware-defined windows; command-with-size rejects more than four dwords in or out. `pwr_reg_rdwr()` allows up to five logical register addresses but copies through a fixed 20-byte buffer. Callers may sleep and must not use APIs in atomic context. Interrupt status clearing relies on writing status with `IPC_STATUS_IRQ`.

Test signals: provider registration should create `/sys/class/intel_scu_ipc/intel_scu_ipc`; register access APIs should serialize and return firmware errors; IRQ and polling modes should both complete commands; unregister should set `ipcdev = NULL` and release resources after references drain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_ipc.c -->
