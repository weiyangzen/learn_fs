# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvconsole.h

Purpose: Declares low-level pSeries LPAR hypervisor console get/put helpers for virtual terminal devices.

Important APIs, types, and functions: Defines `MAX_VIO_PUT_CHARS` and `SIZE_VIO_GET_CHARS` as 16-byte firmware transfer limits. Exposes `hvc_get_chars()`, `hvc_put_chars()`, and `hvc_vio_init_early()`.

Control flow: Console drivers call get/put wrappers with a vterm number and buffer. Early boot can initialize HVC VIO before the full device model is available.

State and persistence: No state in the header. Console state lives in hvc/vio driver structures and firmware terminal queues.

Dependencies and integration points: Integrates with hvc console, pSeries VIO firmware, and early console setup.

Risks: Firmware transfer size is capped at 16 bytes, so callers must handle short I/O. Early initialization runs before normal allocation/device discovery.

Test signals: Early console output, runtime HVC read/write, transfer sizes above and below 16 bytes, vterm absence, and boot with console as primary device.
