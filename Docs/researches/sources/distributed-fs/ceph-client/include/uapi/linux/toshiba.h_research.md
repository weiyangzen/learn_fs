# sources/distributed-fs/ceph-client/include/uapi/linux/toshiba.h

Purpose: Provides the historical userspace ABI for Toshiba laptop SMM/ACPI access through `/proc` and character devices.

Important APIs/types/functions: Path macros identify `TOSH_PROC`, `TOSH_DEVICE`, `TOSHIBA_ACPI_PROC`, and `TOSHIBA_ACPI_DEVICE`. The `SMMRegisters` typedef is a packed/aligned register block carrying CPU register-style fields (`eax`, `ebx`, `ecx`, `edx`, `esi`, `edi`) for firmware calls. Ioctls `TOSH_SMM` and `TOSHIBA_ACPI_SCI` use `_IOWR('t', ...)` with that register block.

Control flow: Userspace opens the Toshiba device node and issues ioctl calls with a populated register block. The driver copies the block, performs a firmware/SMM or ACPI SCI operation, then copies updated register values back.

State and persistence behavior: No state is held in the header. Runtime state is firmware/platform-specific and may change hardware settings immediately; persistence depends on firmware and platform policy.

Dependencies and integration points: Depends on Linux ioctl encoding and the Toshiba laptop driver. The ABI must preserve structure packing because firmware calls map directly to register values.

Risks: Firmware access is privileged and platform-specific; invalid register combinations can fail unpredictably or affect hardware. ABI packing/alignment is critical across compilers and architectures.

Test signals: Build ioctl clients on 32/64-bit, verify `sizeof(SMMRegisters)` and ioctl numbers, run on supported Toshiba hardware or mocked driver paths, and test invalid command handling.
