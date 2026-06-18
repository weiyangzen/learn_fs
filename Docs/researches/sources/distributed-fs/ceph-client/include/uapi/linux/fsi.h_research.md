# sources/distributed-fs/ceph-client/include/uapi/linux/fsi.h

This header defines userspace ioctls for the FSI subsystem, especially raw SCOM access and SBEFIFO control. It is used by low-level service/debug tools for POWER/OpenBMC-style hardware management paths.

Important exports include `struct scom_access`, SCOM interface error flags `SCOM_INTF_ERR_*`, PIB status values `SCOM_PIB_*`, check/reset flags `SCOM_CHECK_*` and `SCOM_RESET_*`, and ioctls `FSI_SCOM_CHECK`, `FSI_SCOM_READ`, `FSI_SCOM_WRITE`, and `FSI_SCOM_RESET`. The file also defines `/dev/sbefifo*` ioctl structures and command constants for controlling SBE FIFO behavior.

Control flow is ioctl based: userspace opens SCOM or SBEFIFO character devices, checks support/protection, issues raw reads/writes with address/data/mask, interprets interface and PIB status, or resets the interface/PIB. State lives in FSI master/slave drivers, SCOM engines, secure boot/protection state, and hardware FIFOs. Persistence is hardware-side register effects, not file data.

Dependencies include `linux/types.h`, `linux/ioctl.h`, FSI core drivers, SCOM/SBE hardware, OpenBMC platform support, and secure-boot policy. Integration points include service processors, chip diagnostics, firmware update/debug tools, and platform bring-up workflows.

Risks include hardware register corruption, secure-boot bypass attempts, future error bits requiring conservative handling, partial writes through masks, timeout/reset side effects, and ABI size changes in low-level structs. Test signals include FSI driver selftests, hardware or simulator SCOM read/write tests, protected-interface tests, reset-path validation, and error/status decode tests.
