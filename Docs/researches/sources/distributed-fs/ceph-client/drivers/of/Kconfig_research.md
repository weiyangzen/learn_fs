# sources/distributed-fs/ceph-client/drivers/of/Kconfig

Purpose: Kconfig definitions for Linux Device Tree/Open Firmware infrastructure.

Important APIs/types/functions: defines core `menuconfig OF` and feature symbols including `OF_UNITTEST`, `OF_KUNIT_TEST`, `OF_ALL_DTBS`, `OF_FLATTREE`, `OF_EARLY_FLATTREE`, `OF_DYNAMIC`, `OF_ADDRESS`, `OF_IRQ`, `OF_RESERVED_MEM`, `OF_RESOLVE`, `OF_OVERLAY`, `OF_OVERLAY_KUNIT_TEST`, and `OF_NUMA`.

Control flow: Kconfig dependencies/selects drive which OF source files build. `OF_EARLY_FLATTREE` defaults on for most OF platforms and selects `OF_FLATTREE`; `OF_ADDRESS` defaults on except SPARC when `HAS_IOMEM` or UML is present; overlay/unit-test options select required resolver/dtc support.

State/persistence: no runtime state; persistent effect is the generated kernel configuration and compiled object set.

Dependencies/integration: consumed by `drivers/of/Makefile` and architecture/platform Kconfig selections. Test options integrate with KUnit and boot-time OF unittest infrastructure.

Risks: `OF_UNITTEST` help explicitly warns it taints the kernel and can corrupt the live devicetree; it should remain development-only. Select chains can pull in DTC/LIBFDT/CRC32 and alter build footprint.

Test signals: config matrix builds for OF disabled/enabled, KUnit tests, overlays, all-DTB compile testing, and architecture exclusions for early flattree/address support.
