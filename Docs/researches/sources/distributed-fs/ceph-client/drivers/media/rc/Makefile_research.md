<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/rc/Makefile

Purpose: kbuild recipe for the remote-controller subsystem, protocol decoders, keymaps, and hardware drivers.

Important APIs and entries: `rc-core-y := rc-main.o rc-ir-raw.o`, with optional `lirc_dev.o`, CEC keymap support, and `bpf-lirc.o`. It always descends into `keymaps/`. It maps each `CONFIG_IR_*` decoder/device and `CONFIG_RC_*` driver to the matching object, and descends into `img-ir/` for `CONFIG_IR_IMG`.

Control flow: selected Kconfig symbols determine object inclusion. The file intentionally keeps decoder and standalone driver lists alphabetically sorted by Kconfig name.

State and persistence: no runtime state; build composition only.

Dependencies and integration points: depends on symbols from `drivers/media/rc/Kconfig` and child Kconfig files. The core object aggregates LIRC and BPF support when enabled rather than building them as unrelated modules.

Risks: breaking alphabetical order is a maintainability issue flagged by comments. Adding a Kconfig symbol without a matching object entry produces a visible configuration that builds no code. Optional `rc-core-*` additions must match symbols that are valid when `RC_CORE` is selected.

Test signals: targeted builds for each listed driver/decoder, `make W=1` for object lists, and Kconfig-to-Makefile consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/Makefile -->
