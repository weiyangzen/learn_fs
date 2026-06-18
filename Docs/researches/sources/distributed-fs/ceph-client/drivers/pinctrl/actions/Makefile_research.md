# sources/distributed-fs/ceph-client/drivers/pinctrl/actions/Makefile

## Purpose
kbuild mapping for Actions Semi OWL pinctrl objects.

## APIs, Flow, And State
Rules map `CONFIG_PINCTRL_OWL` to `pinctrl-owl.o`, `CONFIG_PINCTRL_S500` to `pinctrl-s500.o`, `CONFIG_PINCTRL_S700` to `pinctrl-s700.o`, and `CONFIG_PINCTRL_S900` to `pinctrl-s900.o`. Since the symbols are bool, selected objects build into the kernel image. There is no runtime state in this file.

## Dependencies And Integration
Integrates with `drivers/pinctrl/actions/Kconfig` and parent `obj-y += actions/` traversal. The variant objects rely on the common OWL object being selected by Kconfig dependencies.

## Risks And Tests
Symbol/object drift or missing common support would cause build failures. Test no-object builds when disabled, OWL-only, and each S500/S700/S900 variant under compile-test.
