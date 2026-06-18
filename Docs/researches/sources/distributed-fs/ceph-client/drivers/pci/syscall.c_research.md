# sources/distributed-fs/ceph-client/drivers/pci/syscall.c

## Purpose
`syscall.c` implements legacy `pciconfig_read` and `pciconfig_write` syscalls for direct PCI configuration-space access on architectures that expose them.

## Important APIs, types, and functions
The file defines `SYSCALL_DEFINE5(pciconfig_read, ...)` and `SYSCALL_DEFINE5(pciconfig_write, ...)`. It uses `pci_get_domain_bus_and_slot()`, `pci_user_read_config_byte/word/dword()`, `pci_user_write_config_byte/word/dword()`, `put_user()`, `get_user()`, `capable(CAP_SYS_ADMIN)`, and `security_locked_down(LOCKDOWN_PCI_ACCESS)`.

## Control flow and behavior
Both syscalls target domain 0 only and locate a device by bus and devfn. Reads require `CAP_SYS_ADMIN`, accept lengths 1, 2, or 4, read through PCI user config helpers, and copy the result to userspace. On errors, read writes all ones of the requested width to the user buffer for legacy XFree86 compatibility before returning the errno. Writes require `CAP_SYS_ADMIN` and must not be blocked by kernel lockdown, copy the value from userspace, perform the corresponding config write, and translate PCI config-access failures to `-EIO`.

## State and persistence
No private state is stored. The syscalls can mutate PCI configuration space on writes. Device references acquired by lookup are released before return.

## Dependencies and integration points
It depends on the PCI search helpers in `search.c`, Linux capability checks, lockdown LSM policy, user-copy APIs, and architecture syscall tables.

## Risks
This is a privileged raw hardware access ABI. Reads do not check lockdown, while writes do. Domain 0 targeting is a limitation. The error path intentionally attempts user writes even after earlier failures for ABI compatibility.

## Test signals
Validate permissions without `CAP_SYS_ADMIN`, lockdown write denial, invalid lengths, nonexistent devices, user-copy faults, config read/write error paths, and compatibility behavior where failed reads return all-ones data for sizes 1/2/4.
