# sources/distributed-fs/ceph-client/drivers/accessibility/Makefile Research

## Purpose
This Makefile connects the accessibility subtree to kbuild. It always descends into `braille/` and conditionally descends into `speakup/` when `CONFIG_SPEAKUP` is enabled.

## Important Build Rules And Control Flow
`obj-y += braille/` causes kbuild to visit the braille directory, where the braille object's own config guard decides whether code is emitted. `obj-$(CONFIG_SPEAKUP) += speakup/` adds the Speakup subtree as built-in or module according to the tristate value. Lower-level Makefiles map concrete objects to configuration symbols.

## State And Persistence
No runtime state exists. Persistent state comes from generated build artifacts and `.config` values. The file's main contract is source-tree topology: `braille/` is always considered, while `speakup/` only participates when configured.

## Dependencies And Integration Points
It depends on kbuild's `obj-y` and `obj-$()` conventions and integrates with `drivers/accessibility/braille/Makefile` and `drivers/accessibility/speakup/Makefile`.

## Risks
Removing unconditional braille descent would prevent `CONFIG_A11Y_BRAILLE_CONSOLE` from building. Making Speakup unconditional would expose object rules without their intended configuration guard.

## Test Signals
Build matrix checks should cover `CONFIG_A11Y_BRAILLE_CONSOLE=y`, `CONFIG_SPEAKUP=y`, `CONFIG_SPEAKUP=m`, and both disabled. `make V=1 drivers/accessibility/` should show expected subtree traversal.
