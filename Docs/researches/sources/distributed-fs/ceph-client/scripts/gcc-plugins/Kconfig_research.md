# sources/distributed-fs/ceph-client/scripts/gcc-plugins/Kconfig

Purpose: Defines kernel configuration switches for GCC plugin support and the latent entropy plugin.

Important APIs/options: `HAVE_GCC_PLUGINS` is selected by supported architectures. `GCC_PLUGINS` depends on architecture support, GCC compiler selection, and existence of GCC plugin headers from `$(CC) -print-file-name=plugin`. `GCC_PLUGIN_LATENT_ENTROPY` enables entropy instrumentation.

Control flow: Kconfig exposes the menu only when dependencies pass; latent entropy appears under `if GCC_PLUGINS`.

State/persistence: Affects generated `.config` and therefore build flags/plugin selection.

Dependencies/integration: Depends on Kconfig shell success checks, compiler identity, and plugin header paths. References documentation under `Documentation/kbuild/gcc-plugins.rst`.

Risks: Header existence probe can be fooled by dummy tools or broken GCC plugin installs. Only latent entropy is present in this snippet, while other plugin files may be selected elsewhere or in different tree versions.

Test signals: Kconfig with real GCC plugin headers, Clang/CC_IS_GCC false, unsupported architecture, dummy tools, and latent entropy selection visibility.
