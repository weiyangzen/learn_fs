# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/Kconfig

Purpose: Kconfig menu for DPAA1 QBMan support, including BMan/QMan framework and self-tests.

Important configuration: `FSL_DPAA` is a menuconfig depending on supported Freescale/Layerscape architectures with 64-bit DMA addresses and selects `GENERIC_ALLOCATOR`. It enables BMan and QMan infrastructure. Optional `FSL_DPAA_CHECKING` adds runtime API assertions. `FSL_BMAN_TEST` and `FSL_QMAN_TEST` build self-test modules; API and stash tests refine coverage.

Control flow and integration: these options gate compilation of BMan/QMan CCSR, portals, high-level APIs, shared DPAA helpers, and tests.

State and persistence: no runtime state; configuration controls object inclusion and assertion behavior.

Risks and test signals: risks include enabling DPAA without proper DMA address width or genalloc support. Test signals are DPAA platform builds, self-test module availability, and optional checking warnings during stress.
