# sources/distributed-fs/ceph-client/scripts/gcc-plugins/Makefile

Purpose: Builds GCC plugin shared objects and generated support headers for kernel GCC plugin infrastructure.

Important APIs/rules: Generates `randomize_layout_seed.h` from `scripts/basic/randstruct.seed` with private warning comments. Computes `GCC_PLUGINS_DIR` from `$(CC) -print-file-name=plugin`. Defines `plugin_cxxflags`, `plugin_ldflags`, single-file and multi-file plugin rules, object rules, and touches `include/generated/gcc-plugins.h` after plugin build.

Control flow: `always-y += $(GCC_PLUGIN)` drives selected plugin targets. Single-file plugins compile directly from `.c` to `.so` with `HOSTCXX`; multi-file plugins compile objects then link. Dependency files are generated through `if_changed_dep`.

State/persistence: Produces plugin `.so`, `.o`, generated seed header, dependency files, and generated `gcc-plugins.h`. The seed header embeds the randstruct seed and must remain private.

Dependencies/integration: Kbuild, host C++ compiler, GCC plugin include dir, kernel compiler-version header, selected `GCC_PLUGIN` variables, and `randstruct.seed`.

Risks: Seed exposure weakens randstruct layout secrecy. Host compiler/GCC plugin header version mismatch can break builds. Treating `.c` as host C++ plugin code requires GCC-plugin-compatible source style.

Test signals: Build single and multi-object plugins, seed regeneration when seed changes, out-of-tree object paths, dependency tracking, and clean-files behavior.
