# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-div6.h

Purpose: This header declares the internal Renesas DIV6 registration helper.

Important APIs, types, and functions: It exposes `struct clk *cpg_div6_register(const char *name, unsigned int num_parents, const char **parent_names, void __iomem *reg, struct raw_notifier_head *notifiers);`. The include guard is `__RENESAS_CLK_DIV6_H__`.

Control flow: SoC or family CPG drivers include this header when they need to create DIV6 clocks from already-mapped CPG registers instead of relying on a standalone DT node.

State and persistence: No state. The function it declares creates state in `clk-div6.c`.

Dependencies and integration: The declaration references `struct clk`, `void __iomem`, and `struct raw_notifier_head`, relying on includers or prior headers for full declarations. It integrates with Renesas CPG helper code and the Linux CCF.

Risks: This is a minimal internal header. API changes must be synchronized with all Renesas CPG users. Because the helper accepts mutable `parent_names`, callers should not pass const storage they cannot tolerate being compacted by the implementation.

Test signals: Compile all Renesas drivers that include the header, especially Gen2/legacy CPG files using DIV6 registration, and verify no prototype mismatch warnings.
