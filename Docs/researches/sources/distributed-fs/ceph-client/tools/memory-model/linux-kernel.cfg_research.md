# sources/distributed-fs/ceph-client/tools/memory-model/linux-kernel.cfg

Purpose: Herd/LKMM configuration file selecting the Linux-kernel memory model, macro definitions, Bell/Cat model files, variant, graph layout, event visibility, and edge rendering attributes.

Important APIs/types/functions: Configuration keys include `macros linux-kernel.def`, `bell linux-kernel.bell`, `model linux-kernel.cat`, `variant lkmmv2`, graph/display settings, and colored `edgeattr` entries for relations such as `hb`, `co`, `mb`, `wmb`, and `rmb`.

Control flow: Consumed by herd7/litmus tooling rather than executed. Tools read the file to configure model evaluation and generated graph output.

State and persistence: Static configuration. No runtime state.

Dependencies/integration: Integrates with `tools/memory-model` scripts and herdtools7. Referenced model/macro files must exist relative to the memory-model directory.

Risks: Changes alter formal verification semantics and visualization. Missing referenced files or unsupported keys break herd runs. Display settings can affect graph readability but not model result.

Test signals: Run representative LKMM litmus tests with `herd7 -conf linux-kernel.cfg` through existing scripts and compare expected `Result:` annotations.
