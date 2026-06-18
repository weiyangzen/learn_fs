# sources/distributed-fs/ceph-client/drivers/sh/clk/Makefile

Purpose: Kbuild file for the legacy SuperH clock framework.

Important build rules: `core.o` is always built when the directory is selected, and `cpg.o` is added by `CONFIG_SH_CLK_CPG`.

Control flow and integration: the parent Makefile selects this directory for legacy `CONFIG_HAVE_CLK` systems without `CONFIG_COMMON_CLK`. Platform clock definitions then link against `core.o` APIs and optionally CPG helpers.

State and dependencies: no runtime state in this file. Dependencies are Kbuild and the `CONFIG_SH_CLK_CPG` symbol. Risks are mismatched platform expectations if CPG users build without `cpg.o`, or accidental coexistence with common-clk code. Test signals are successful SH legacy-clock builds and exported symbol resolution for `clk_register`, `sh_clk_mstp_register`, and div helpers.
