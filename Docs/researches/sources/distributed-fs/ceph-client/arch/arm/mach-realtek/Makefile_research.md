# sources/distributed-fs/ceph-client/arch/arm/mach-realtek/Makefile

Purpose: unconditional object list for Realtek machine support once the directory is selected.

Important APIs/types/functions: builds `rtd1195.o`.

Control flow: make-time object inclusion only.

State and persistence: none.

Dependencies and integration points: links the RTD1195 `DT_MACHINE_START` descriptor into ARM machine discovery.

Risks: any future Realtek SoC support needs explicit object additions; current file assumes the directory is only entered for relevant configs.

Test signals: build with `ARCH_REALTEK=y` and verify `rtd1195` machine descriptor is linked.
