# sources/distributed-fs/ceph-client/drivers/clk/mmp/reset.h

Purpose: private MMP reset-controller header.

Important APIs/types: defines `MMP_RESET_INVERT`, `struct mmp_clk_reset_cell`, `struct mmp_clk_reset_unit`, and the `mmp_clk_reset_register` prototype or stub depending on `CONFIG_RESET_CONTROLLER`.

Control flow: no runtime flow in the header. The stub makes SoC clock files build when reset-controller support is disabled.

State and persistence: cell descriptors carry clock ID, register address, reset bits, flags, and optional spinlock. The unit embeds a `reset_controller_dev`.

Dependencies and integration: includes Linux reset-controller types and is used by MMP SoC clock init files plus `reset.c`.

Risks: the invert flag is part of the interface but not honored by `reset.c`, which can mislead table authors. Header users need `struct device_node` visibility through other includes.

Test signals: build coverage with and without `CONFIG_RESET_CONTROLLER`, and reset phandle tests for SoC clock providers.
