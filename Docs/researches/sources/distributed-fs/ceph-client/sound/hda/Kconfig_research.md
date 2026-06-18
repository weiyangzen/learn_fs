# sources/distributed-fs/ceph-client/sound/hda/Kconfig

## Purpose

This Kconfig file defines the top-level "HD-Audio" menu and includes the HDA common, controller, codec, and core configuration subtrees.

## Important APIs, types, and functions

It uses Kconfig `menu`, `source`, and `endmenu` directives. The included files are `sound/hda/common/Kconfig`, `sound/hda/controllers/Kconfig`, `sound/hda/codecs/Kconfig`, and `sound/hda/core/Kconfig`.

## Control flow

During kernel configuration, entering the HD-Audio menu exposes symbols from the sourced subtrees. Ordering places common/controller/codecs/core symbols under the same menu but leaves individual dependencies to those files.

## State and persistence behavior

There is no runtime state. The persistent effect is the generated kernel `.config` choices and build graph.

## Dependencies and integration points

This is the integration root for the HDA subsystem configuration. It must align with the HDA Makefile directory layout.

## Risks and test signals

Risks are missing sourced subtrees after directory refactors or symbols hidden by menu placement. Test signals are `make menuconfig`, `olddefconfig`, and builds for configurations enabling HDA controllers/codecs.
