## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-stm32.h

Purpose: Shared STM32MP25 PCIe definitions for the RC and EP drivers. It centralizes the private-data lookup macro and SYSCFG register fields used to select controller mode and LTSSM state.

Important APIs, types, and functions: `to_stm32_pcie(x)` maps a `dw_pcie` instance back to driver private data through `dev_get_drvdata((x)->dev)`. `STM32MP25_PCIECR_TYPE_MASK`, `STM32MP25_PCIECR_EP`, `STM32MP25_PCIECR_RC`, and `STM32MP25_PCIECR_LTSSM_EN` define the mode and link-training bits in `SYSCFG_PCIECR`. `SYSCFG_PCIECR` is the syscfg offset used by both drivers.

Control flow: this header has no runtime flow. It is included by `pcie-stm32.c` and `pcie-stm32-ep.c`, which use the constants during probe, link start/stop, and PERST handling.

State and persistence: the header defines volatile register bits only. It stores no state and has no persistence behavior.

Dependencies and integration points: depends on Linux bit macros and device APIs. It forms the interface between STM32 DesignWare glue code and the system configuration regmap named by the platform drivers.

Risks: mode values are asymmetric: EP is encoded as zero while RC is `BIT(10)` within a wider `GENMASK(11, 8)` type field. Callers must use `regmap_update_bits()` with the full type mask or stale mode bits can survive. The lookup macro assumes `platform_set_drvdata()` points to the enclosing `struct stm32_pcie`.

Test signals: compile coverage for both STM32 RC and EP drivers, and runtime verification that syscfg writes put the controller into the expected RC or EP mode and that LTSSM toggling affects link training.
