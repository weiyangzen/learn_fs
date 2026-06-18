# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/Makefile

Purpose: maps Lantiq/MaxLinear DSA Kconfig symbols to object files.

Important APIs/types/functions: builds `lantiq_gswip.o`, `lantiq_gswip_common.o`, and `mxl-gsw1xx.o` for their corresponding Kconfig symbols.

Control flow: no runtime flow; Kbuild includes objects according to configuration.

State and persistence: no runtime state; affects the build graph.

Dependencies and integration: object mapping matches Kconfig, and both chip drivers rely on common code exporting `gswip_probe_common()`.

Risks and test signals: object naming drift or missing common linkage. Test with both GSWIP and GSW1xx as modules and built-ins.
