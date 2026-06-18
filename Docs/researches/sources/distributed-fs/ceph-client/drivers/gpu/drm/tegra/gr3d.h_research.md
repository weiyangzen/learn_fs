# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr3d.h

Purpose: defines GR3D address-register offsets and register-count bound used by firewall validation.

Important APIs/types: macros generate indexed attribute, texture, global surface, overflow surface, and sampler surface address registers, plus fixed Z/tag/output address registers. `GR3D_NUM_REGS` sizes the address bitmap.

Control flow and state: no executable logic; constants are consumed by `gr3d_addr_regs[]`.

Dependencies/integration: integrated with `gr3d.c` firewall callbacks and host1x submit validation.

Risks: register macro arithmetic must match hardware class layout. Missing address-register definitions allow unchecked command-stream pointers.

Test signals: firewall tests for representative indexed ranges and static review against hardware class docs.
