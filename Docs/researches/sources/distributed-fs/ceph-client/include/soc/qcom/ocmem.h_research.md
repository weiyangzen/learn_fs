# sources/distributed-fs/ceph-client/include/soc/qcom/ocmem.h

Purpose: declares the Qualcomm OCMEM allocator API for on-chip memory used by performance, latency, and power-sensitive clients such as GPU, camera/video, and audio blocks.

Important APIs/types/functions: defines `enum ocmem_client` with `OCMEM_GRAPHICS`, opaque `struct ocmem`, and `struct ocmem_buf` containing `offset`, `addr`, and `len`. When `CONFIG_QCOM_OCMEM` is enabled it exports `of_get_ocmem`, `ocmem_allocate`, and `ocmem_free`; otherwise it provides disabled stubs.

Control flow: clients get the OCMEM provider from device tree, allocate a buffer for a client ID and size, use the returned physical/address window, and release it with `ocmem_free`. Disabled builds fail with `ERR_PTR(-ENODEV)`.

State and persistence: state is allocator-owned OCMEM address space and per-client allocations. Buffers persist until explicitly freed or provider teardown.

Dependencies and integration: depends on `linux/device.h` and `linux/err.h`. Implementation is in `drivers/soc/qcom/ocmem.c`; consumers include MSM Adreno GPU code and SCM OCMEM lock/unlock paths.

Risks: limited client support, allocation lifetime leaks, and address/offset confusion can starve clients or program firmware with wrong ranges. Test signals include GPU probe/use on OCMEM SoCs, allocation/free failure paths, and disabled-config builds.
