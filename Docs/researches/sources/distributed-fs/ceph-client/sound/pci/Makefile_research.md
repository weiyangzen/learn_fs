# sources/distributed-fs/ceph-client/sound/pci/Makefile

## Purpose

This Makefile maps top-level ALSA PCI Kconfig symbols to kbuild module objects and includes PCI sound subdirectories.

## Important APIs, Types, and Functions

It defines single- or multi-object module composition for legacy PCI drivers, such as `snd-ad1889-y := ad1889.o`, `snd-ens1370-y := ens1370.o ak4531_codec.o`, and similar assignments for ALS300, ALS4000, ATI IXP, AZT3328, Bt87x, CMI, CS4281, CS5530, Ensoniq, ESS, FM801, Intel8x0, Maestro3, RME, SiS, SonicVibes, and VIA. It then adds objects with `obj-$(CONFIG_SND_...) += snd-...o`.

The final `obj-$(CONFIG_SND) +=` list descends into subdirectories: `ac97`, `ali5451`, `asihpi`, `au88x0`, `aw2`, `ctxfi`, `ca0106`, `cs46xx`, `cs5535audio`, `lola`, `lx6464es`, `echoaudio`, `emu10k1`, `ice1712`, `korg1212`, `mixart`, `nm256`, `oxygen`, `pcxhr`, `riptide`, `rme9652`, `trident`, `ymfpci`, and `vx222`.

## Control Flow

For each enabled `CONFIG_SND_*`, kbuild composes the corresponding module from its `snd-*-y` object list. Subdirectories are visited whenever ALSA sound support is enabled, leaving each child directory to decide whether to build objects based on its own config symbols.

## State and Persistence

The file has no runtime state. It determines module names, linked objects, and recursive build traversal.

## Dependencies and Integration Points

It depends on `sound/pci/Kconfig` for symbols and on child Makefiles such as `sound/pci/ac97/Makefile`. It also links shared companion objects, for example `ak4531_codec.o` into `snd-ens1370.o`.

## Risks and Edge Cases

Adding a Kconfig option without a matching Makefile object, or vice versa, causes silent build omission or dead entries. The unconditional subdirectory descent under `CONFIG_SND` means child Makefiles must be correct even when PCI-specific symbols are off. Module names in help text should stay synchronized with `snd-*` object names.

## Test Signals

Build with each listed `CONFIG_SND_*` as `m`, allmodconfig for subdirectory traversal, and targeted dependency checks for multi-object modules like `snd-ens1370`.
