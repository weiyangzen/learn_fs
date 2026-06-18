# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h

Purpose: Declares the DCN31 VPG wrapper, extending DCN30-style generic packet registers with memory power control.

Important APIs/types/functions: `VPG_DCN31_REG_LIST()` lists generic packet/status/update registers plus `VPG_MEM_PWR`. Field macros include the 15 generic packet frame/immediate update bits and `VPG_GSP_MEM_LIGHT_SLEEP_DIS`, `VPG_GSP_LIGHT_SLEEP_FORCE`, and `VPG_GSP_MEM_PWR_STATE`. `struct dcn31_vpg` mirrors DCN30 with DCN31 register metadata.

Control flow: Header declarations only.

State/persistence: Stores immutable register/shift/mask pointers and the inherited `struct vpg` base.

Dependencies/integration: Includes `vpg.h`; implemented by `dcn31_vpg.c` and integrated with DCN31 resource construction.

Risks: Duplicates much of DCN30 VPG metadata, so changes to generic packet slots must be mirrored. Missing memory-power fields would compile but disable low-power hooks.

Test signals: Compile-time resource expansion and register traces for packet slots plus VPG memory power transitions.
