# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/Makefile

## Purpose
`side-codecs/Makefile` maps side-codec Kconfig symbols to kernel objects for shared libraries, component glue, and vendor amplifier drivers under the HD-audio codec tree.

## APIs, Types, and Functions
This file defines object composition rather than functions. It adds `-I$(src)/../../common` to subdirectory CFLAGS and defines object lists such as `snd-hda-cirrus-scodec-y`, `snd-hda-scodec-cs35l41-y`, `snd-hda-scodec-cs35l41-i2c-y`, `snd-hda-scodec-cs35l56-y`, `snd-hda-scodec-component-y`, and TAS2781 variants.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_...)` lines to include the selected side-codec objects. Core drivers such as CS35L41 and CS35L56 are built from common HDA implementation files plus property/shared files, while I2C/SPI wrappers build bus-specific probe modules. The component glue is controlled by `CONFIG_SND_HDA_SCODEC_COMPONENT`.

## State and Persistence Behavior
The Makefile has build-time state only. Object membership determines module names, link boundaries, exported namespace availability, and which side-codec code can bind at runtime.

## Dependencies and Integration Points
It integrates with the `Kconfig` symbols in the same directory and with source files such as `cirrus_scodec.c`, `cs35l41_hda.c`, `hda_component.c`, `cs35l56_hda.c`, and `tas2781_hda.c`. The include path supports shared common headers.

## Risks
Kconfig/Makefile symbol drift causes selected features not to build or missing objects at link time. Core/bus object splits must preserve exported symbols and namespaces. Tests depend on `snd-hda-cirrus-scodec-test-y` matching the KUnit source.

## Test Signals
Run representative `allyesconfig`/module builds for side-codec symbols, verify generated module names, ensure no missing exported symbols, and confirm KUnit test object inclusion when `SND_HDA_CIRRUS_SCODEC_KUNIT_TEST` is enabled.
