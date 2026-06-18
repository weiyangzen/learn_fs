# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/drv_types_sdio.h

Purpose: this header defines the SDIO-specific device-interface data embedded in `dvobj_priv`.

Important APIs/types: `struct sdio_data` contains the SDIO function number, TX/RX block-mode flags, `block_transfer_len`, the kernel `struct sdio_func *func`, and an opaque `sys_sdio_irq_thd` pointer for the SDIO IRQ thread. The header includes Linux MMC SDIO function and ID headers.

Control flow and integration: there is no executable code. `drv_types.h` embeds `struct sdio_data intf_data` in `dvobj_priv`. `sdio_ops.c` uses `block_transfer_len` to round port transfers and `func` indirectly through device conversion. `rtl8723bs_interface_configure` maps SDIO output pipes in `dvobj_priv`, while lower-level SDIO probe code is expected to initialize `sdio_data`.

State and persistence: `sdio_data` persists for the lifetime of the device object and is shared by adapters attached to the same SDIO function. It stores host-transfer geometry used by all IO paths.

Dependencies: depends on Linux MMC SDIO core types. Consumers assume `func` is valid for firmware loading device lookup and SDIO command execution.

Risks and test signals: incorrect `block_transfer_len` leads to under/over-rounded RX/TX port transfers. IRQ-thread ownership and teardown must be coordinated with adapter stop/removal. Tests should cover block sizes from the host controller, probe/remove, runtime suspend/resume, and concurrent TX/RX access through shared `dvobj_priv.intf_data`.
