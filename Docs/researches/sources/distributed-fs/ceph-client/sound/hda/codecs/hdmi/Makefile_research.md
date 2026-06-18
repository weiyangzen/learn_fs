# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/Makefile

## Purpose
Maps HDMI/DisplayPort HDA codec Kconfig symbols to the object files and modules that implement generic, simple, and vendor-specific HDMI audio support.

## Important APIs, Types, and Functions
The Makefile adds `-I$(src)/../../common` to subdirectory C flags. It defines composite objects: `snd-hda-codec-hdmi-y := hdmi.o eld.o`, `snd-hda-codec-simplehdmi-y := simplehdmi.o`, `snd-hda-codec-intelhdmi-y := intelhdmi.o`, `snd-hda-codec-atihdmi-y := atihdmi.o`, `snd-hda-codec-nvhdmi-y := nvhdmi.o`, `snd-hda-codec-nvhdmi-mcp-y := nvhdmi-mcp.o`, and `snd-hda-codec-tegrahdmi-y := tegrahdmi.o`. The `obj-$(CONFIG_...)` lines connect these composites to Kconfig symbols.

## Control Flow
Kbuild evaluates each `obj-$(CONFIG_*)` assignment and builds the relevant module or built-in object. Generic HDMI combines the main HDMI implementation with ELD helper code. Vendor-specific drivers compile as separate modules that import or call generic HDMI support depending on their C implementation and Kconfig selection.

## State and Persistence Behavior
The file has no runtime state. Its persistent effect is the kernel build graph and the final set of built-in objects or loadable modules.

## Dependencies and Integration Points
It integrates with the HDMI Kconfig file and kbuild's composite object convention. The include path gives HDMI codec code access to common HDA helpers. The generic object depends on both `hdmi.o` and `eld.o`, so ELD routines are packaged with generic HDMI support.

## Risks
Risks are build-graph mismatches: omitting `eld.o` from the generic object would break ELD symbols, associating an object with the wrong config would build unsupported drivers, and include-path changes could hide shared headers. Vendor modules also rely on Kconfig selecting the correct base support to avoid unresolved imports.

## Test Signals
Build all HDMI configs as built-in and module, inspect `modules.order` or linked objects for expected `snd-hda-codec-hdmi`, `simplehdmi`, `intelhdmi`, `atihdmi`, `nvhdmi`, `nvhdmi-mcp`, and `tegrahdmi` outputs, and run modpost to catch missing imports or namespace annotations.
