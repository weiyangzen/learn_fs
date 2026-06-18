# sources/distributed-fs/ceph-client/drivers/firmware/imx/Kconfig

Purpose: Defines NXP i.MX firmware driver configuration for DSP IPC, legacy SCU mailbox RPC, and newer SCMI protocol wrapper drivers.

Important APIs/types/functions: Symbols are `IMX_DSP`, `IMX_SCU`, `IMX_SCMI_CPU_DRV`, `IMX_SCMI_LMM_DRV`, and `IMX_SCMI_MISC_DRV`. Dependencies select mailbox support, SoC bus support, and ARM MXC/compile-test availability.

Control flow: No runtime flow. The settings determine whether host-to-DSP mailbox, SCFW mailbox RPC, and SCMI CPU/LMM/MISC helper exports are built.

State and persistence behavior: No state. Build choices decide which firmware communication stacks and exported helper APIs are available to platform drivers.

Dependencies and integration points: Integrates i.MX mailbox controller support, `SOC_BUS`, SCMI protocol framework, and platform-specific firmware headers.

Risks and test signals: Incorrect default/module choices can leave dependent drivers without exported symbols or probe sequencing. Test allmodconfig, ARCH_MXC default builds, modular SCMI wrappers, and compile-test builds.
