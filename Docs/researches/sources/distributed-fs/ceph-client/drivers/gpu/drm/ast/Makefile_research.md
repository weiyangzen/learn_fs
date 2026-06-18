## sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/Makefile

Purpose: object list for the AST DRM driver.

Important build composition includes generation-specific files `ast_2000.o` through `ast_2600.o`, cursor, DDC, DP501, ASTDP, core driver, memory manager, mode setting, POST helpers, SIL164, VBIOS, and VGA output. `obj-$(CONFIG_DRM_AST) := ast.o` links these into one module/built-in object.

Control flow and state are build-time. Dependencies are all listed source files and the Kconfig symbol. Integration risks include unresolved symbols if an output path or generation constructor is omitted and overlinking generation code that must remain guarded by runtime chip detection. Test signals are full module link, `modpost` success, and probe paths resolving all selected transmitter/mode helper symbols.
