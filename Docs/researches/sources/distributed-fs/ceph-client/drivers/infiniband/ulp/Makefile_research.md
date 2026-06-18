# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/Makefile

Purpose: Defines the kbuild inclusion map for InfiniBand upper-layer protocol drivers in this source tree. It routes selected kernel configuration symbols to ULP subdirectories.

Important APIs/types/functions: This is a Makefile, not C code. It conditionally includes `ipoib/`, `srp/`, `srpt/`, `iser/`, `isert/`, and `rtrs/` via `obj-$(CONFIG_...) += directory/` assignments.

Control flow: During kernel build, kbuild evaluates each `CONFIG_INFINIBAND_*` symbol. Enabled symbols add the corresponding subdirectory to the build traversal; disabled symbols omit it completely. The file has no runtime control flow.

State and persistence behavior: No runtime state. The only persistent effect is build graph selection from kernel configuration.

Dependencies/integration: Integrates with the parent InfiniBand driver Makefile and each ULP subdirectory Makefile. It depends on Kconfig symbols being defined elsewhere, including the IPoIB symbols in `ulp/ipoib/Kconfig`.

Risks: A missing or misspelled config symbol silently excludes a ULP. Directory order can matter if future build products have implicit dependencies, though these entries are currently independent. Because this file only selects subdirectories, per-driver object composition lives elsewhere.

Test signals: `make olddefconfig` with each ULP enabled/disabled, `make M=drivers/infiniband/ulp`, checking generated built-in/module targets, and confirming IPoIB object traversal only when `CONFIG_INFINIBAND_IPOIB` is set.
