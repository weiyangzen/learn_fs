# sources/distributed-fs/ceph-client/kernel/printk/Makefile

## Purpose

This Makefile is the build manifest for the kernel printk subsystem in this source tree. It selects the core printk implementation unconditionally, then layers optional console safety, non-blocking console support, braille-console support, printk format indexing, sysctl support, and the ringbuffer KUnit test according to Kconfig symbols.

## Important build targets

- `obj-y = printk.o` makes `printk.c` part of the kernel build regardless of `CONFIG_PRINTK`, because that file also provides stubs and console infrastructure used by non-printk builds.
- `obj-$(CONFIG_PRINTK) += printk_safe.o nbcon.o` adds recursion-safe printk support and non-blocking console support only when printk is enabled.
- `obj-$(CONFIG_A11Y_BRAILLE_CONSOLE) += braille.o` adds command-line braille console integration.
- `obj-$(CONFIG_PRINTK_INDEX) += index.o` exposes indexed printk format strings through debugfs.
- `obj-$(CONFIG_PRINTK) += printk_support.o` defines a composite object whose required member is `printk_ringbuffer.o`; `printk_support-$(CONFIG_SYSCTL) += sysctl.o` adds sysctl controls when enabled.
- `obj-$(CONFIG_PRINTK_RINGBUFFER_KUNIT_TEST) += printk_ringbuffer_kunit_test.o` builds the ringbuffer test object.

## Control flow and integration

The build graph keeps the always-needed console/syslog facade in `printk.o` while putting the actual record storage backend in `printk_support.o` only for `CONFIG_PRINTK`. `nbcon.o` is built with printk because its APIs are declared from `internal.h` and called by `printk.c` for console flushing. `braille.o` is independent of general printk enablement but is only selected for accessibility braille console support. `index.o` is tied to `CONFIG_PRINTK_INDEX` and depends on linker-emitted `__start_printk_index` and module section metadata.

## State and persistence behavior

This file has no runtime state. Its main persistence effect is compile-time: it determines which object files become part of vmlinux or built-in kernel objects. Mis-gating an object here can produce missing symbols in one configuration or dead code in another.

## Dependencies

The manifest depends on Kbuild variable conventions and Kconfig symbols: `CONFIG_PRINTK`, `CONFIG_A11Y_BRAILLE_CONSOLE`, `CONFIG_PRINTK_INDEX`, `CONFIG_SYSCTL`, and `CONFIG_PRINTK_RINGBUFFER_KUNIT_TEST`.

## Risks and test signals

`printk.o` must stay unconditional because several public console functions and stubs are needed even when `CONFIG_PRINTK` is disabled. `nbcon.o` must not be built without printk support unless all references and storage backing are stubbed. Build coverage should include `CONFIG_PRINTK=y/n`, `CONFIG_SYSCTL=y/n`, `CONFIG_PRINTK_INDEX=y`, `CONFIG_A11Y_BRAILLE_CONSOLE=y`, and `CONFIG_PRINTK_RINGBUFFER_KUNIT_TEST=y`.
