# sources/distributed-fs/ceph-client/tools/verification/rvgen/rvgen/container.py

Purpose: `container.py` generates a kernel RV monitor container scaffold rather than a concrete automaton monitor.

Important class: `Container` subclasses `generator.RVGenerator` with `template_dir = "container"`. Its constructor reads the container `main.h` template and sets `self.name`. `fill_model_h()` substitutes `%%MODEL_NAME%%`. `fill_kconfig_tooltip()` appends or auto-patches a container-specific Kconfig marker so nested monitors can be inserted under that container.

Control flow and integration: the top-level `rvgen container -n NAME` command constructs this class and calls `print_files()`, which is inherited from `RVGenerator` to create `NAME.c`, `NAME.h`, and `Kconfig`.

State and dependencies: output files are written to a new local directory or kernel RV monitor directory with `--auto_patch`. Dependencies are generic and container templates. Risks include returning silently if the output directory already exists, marker-based auto-patching duplicating entries, and no validation of model name as a C/Kconfig-safe identifier. Test signals are generated container files and Kconfig tooltip/patch containing the new container marker.
