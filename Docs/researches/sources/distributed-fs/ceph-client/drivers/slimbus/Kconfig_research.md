# sources/distributed-fs/ceph-client/drivers/slimbus/Kconfig

Purpose: configuration menu for the Linux SLIMbus framework and the Qualcomm NGD controller.

Important symbols: `SLIMBUS` is a tristate bus framework option. `SLIM_QCOM_NGD_CTRL` selects the Qualcomm Satellite Non-Generic Device controller and depends on IOMEM, DMA engine, NET, QCOM remoteproc/common support or COMPILE_TEST fallback, and ARCH_QCOM or COMPILE_TEST. It selects QMI and PDR helper libraries.

Control flow: enabling the framework builds the core/messaging/scheduling/stream objects. Enabling the Qualcomm controller adds its controller implementation, which plugs into the framework APIs.

State and dependencies: no runtime state. Dependencies include Kconfig, SoC support, DMA, QMI/PDR helpers, and remoteproc integration. Risks are complex dependency combinations for compile-test versus real Qualcomm platforms. Test signals are Kconfig resolution, allmodconfig builds, and expected object/module generation for framework-only and Qualcomm-controller configurations.
